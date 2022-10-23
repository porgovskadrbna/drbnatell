import dotenv
from pilmoji.core import Pilmoji

dotenv.load_dotenv()

import io
import os
import secrets
import textwrap
from uuid import UUID

import aiofiles
import ffmpy
import httpx
from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    RedirectResponse,
    StreamingResponse,
)
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image, ImageFont
from pilmoji import Pilmoji
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


@app.get("/sw.js")
async def swjs():
    return FileResponse("static/sw.js")


admin_auth = HTTPBasic()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    count = await Tells.all().count()

    return templates.TemplateResponse(
        "home.html", {"request": request, "count": count + 1824}
    )


@app.get("/sent", response_class=HTMLResponse)
async def sent(request: Request):
    return templates.TemplateResponse("sent.html", {"request": request})


@app.post("/sent", response_class=HTMLResponse)
async def sent(
    request: Request,
    background_tasks: BackgroundTasks,
    text: str = Form(...),
    media: UploadFile = File(None),
):
    if not text:
        return RedirectResponse("/")

    media.file.seek(0, io.SEEK_END)
    has_media = media.file.tell() > 0
    media.file.seek(0)

    if has_media:
        if media.content_type.startswith("image/"):
            tell = await Tells.create(text=text, has_image=True)
            extension = f".{media.filename.split('.')[-1]}"
            filename = f"uploads/{tell.id}{extension}"
        elif media.content_type.startswith("video/"):
            tell = await Tells.create(text=text, has_video=True)
            extension = f".{media.filename.split('.')[-1]}"
            filename = f"uploads/{tell.id}{extension}"
    else:
        tell = await Tells.create(text=text)

    if has_media:
        async with aiofiles.open(filename, "wb") as image_file:
            while content := await media.read(1024):
                await image_file.write(content)

        if media.content_type.startswith("image/"):
            background_tasks.add_task(process_image, filename, str(tell.id))
        elif media.content_type.startswith("video/"):
            background_tasks.add_task(process_video, filename, str(tell.id))

    background_tasks.add_task(send_notification)

    return templates.TemplateResponse("sent.html", {"request": request})


def process_image(original_file: str, tell_id: str):
    new_file = f"attachments/{tell_id}.png"

    with Image.open(original_file) as image:
        image.save(new_file)

    os.remove(original_file)


def process_video(original_file: str, tell_id: str):
    new_file = f"attachments/{tell_id}.mp4"

    ffmpy.FFmpeg(inputs={original_file: None}, outputs={new_file: None}).run()

    os.remove(original_file)


def send_notification():
    headers = {
        "Authorization": "api_key=a21168592045add8420ed42f18c9b5da",
    }

    httpx.post(
        "https://api.pushalert.co/rest/v1/send",
        headers=headers,
        data={
            "title": "Drbna",
            "message": "Novej drb je tu",
            "url": "https://porgovskadrbna.cz/admin",
        },
    )


def get_admin_auth(credentials: HTTPBasicCredentials = Depends(admin_auth)):
    correct_username = secrets.compare_digest(
        os.getenv("DRBNA_USERNAME"), credentials.username
    )
    correct_password = secrets.compare_digest(
        os.getenv("DRBNA_PASSWORD"), credentials.password
    )

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Co tady sakra zkoušíš?",
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


@app.get("/picture-tell/{id}")
async def picture_tell(id: UUID):
    tell = await TellResponse.from_queryset_single(Tells.get(id=id))
    text = textwrap.fill(
        tell.text, 50, break_long_words=False, replace_whitespace=False
    )

    font = ImageFont.truetype(
        "notosans.ttf", 42, layout_engine="raqm", encoding="unic"
    )

    image = Image.new(
        mode="RGB",
        size=(1200, 160 + len(text.splitlines()) * 60),
        color="#1a222d",
    )

    with Pilmoji(image) as pilmoji:
        pilmoji.text((80, 80), text, font=font, fill="white", spacing=10)

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
