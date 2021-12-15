import dotenv

dotenv.load_dotenv()

import io
import os
import secrets
import textwrap
from uuid import UUID

import aiofiles
from fastapi import (
    BackgroundTasks,
    FastAPI,
    File,
    Form,
    Request,
    UploadFile,
    Depends,
    HTTPException,
    status,
)
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image, ImageDraw, ImageFont
from tortoise.contrib.fastapi import register_tortoise

import db
from models.tells import TellResponse, Tells

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)
app.mount(
    "/attachments",
    StaticFiles(directory="attachments"),
    name="attachments",
)

admin_auth = HTTPBasic()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/sent", response_class=HTMLResponse)
async def sent(request: Request):
    return templates.TemplateResponse("sent.html", {"request": request})


@app.post("/sent", response_class=HTMLResponse)
async def sent(
    request: Request,
    background_tasks: BackgroundTasks,
    text: str = Form(None),
    image: UploadFile = File(None),
):
    if not text:
        return RedirectResponse("/")

    tell = await Tells.create(text=text, has_image=bool(image))
    extension = f".{image.filename.split('.')[-1]}"
    filename = f"uploads/{tell.id}{extension}"

    if image is not None:
        async with aiofiles.open(filename, "wb") as image_file:
            while content := await image.read(1024):
                await image_file.write(content)

    background_tasks.add_task(process_image, filename, str(tell.id))

    return templates.TemplateResponse("sent.html", {"request": request})


def process_image(original_file: str, tell_id: str):
    new_file = f"attachments/{tell_id}.png"

    image = Image.open(original_file)
    image.save(new_file)

    os.remove(original_file)


def get_admin_auth(credentials: HTTPBasicCredentials = Depends(admin_auth)):
    correct_username = secrets.compare_digest(
        os.getenv("USERNAME"), credentials.username
    )
    correct_password = secrets.compare_digest(
        os.getenv("PASSWORD"), credentials.password
    )


@app.get("/admin", response_class=HTMLResponse)
async def admin(
    request: Request,
    _=Depends(get_admin_auth),
):
    tells = await TellResponse.from_queryset(
        Tells.all().order_by("-created_at")
    )

    return templates.TemplateResponse(
        "admin.html", {"request": request, "tells": tells}
    )

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )


@app.get("/picture-tell/{id}")
async def picture_tell(id: UUID):
    tell = await TellResponse.from_queryset_single(Tells.get(id=id))
    text = textwrap.fill(tell.text, 56, break_long_words=False)

    font = ImageFont.truetype("notosans.ttf", 18)
    print(len(text.splitlines()))
    image = Image.new(
        mode="RGB",
        size=(600, 100 + len(text.splitlines()) * 25),
        color="#1a222d",
    )
    draw = ImageDraw.Draw(image)
    draw.text((50, 50), text, font=font, fill="white", spacing=5)
    buf = io.BytesIO()
    image.save(buf, "JPEG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/jpeg")


register_tortoise(
    app,
    config=db.TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)
