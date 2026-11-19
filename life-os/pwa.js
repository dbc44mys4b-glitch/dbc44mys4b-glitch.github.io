/* Installation support. iOS installation uses the Safari Share menu. */
(function(){
  window.LIFEOS_INSTALL_PROMPT=null;
  window.addEventListener('beforeinstallprompt',event=>{
    event.preventDefault();window.LIFEOS_INSTALL_PROMPT=event;
  });
  if('serviceWorker' in navigator && (location.protocol==='https:'||location.hostname==='localhost'||location.hostname==='127.0.0.1')){
    window.addEventListener('load',()=>navigator.serviceWorker.register('./sw.js').catch(e=>console.warn('Offline installation unavailable:',e)));
  }
})();
