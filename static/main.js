if ('serviceWorker' in navigator && 'PushManager' in window) {
  console.log('Service Worker and Push is supported');

  navigator.serviceWorker.register('static/sw.js')
  .then(function(swReg) {
    swRegistration = swReg;
  })
  .catch(function(error) {
    console.error('Service Worker Error', error);
  });
}

navigator.serviceWorker.ready.then(function(registration) {
  registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array("BPnN5tRwF8ZE6C692MCO_fMMRkRdKTosvvX0jO4j0Wbv3Q27AWx-GXXbReEUKo6GnMuU3Jcczo1h")
  })
  .then(function(subscription) {
    savePushSubscription(subscription);
  })
  .catch(function(e) {})
})

