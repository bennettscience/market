function showToast(msg = 'Loading...', timeout = 5000, err = false) {
    const toast = document.querySelector(`#toast`)
    // Handle message objects from hyperscript
    // For non-template returns, the backend will also return JSON with
    // the `message` key with details for the user.
    if(typeof msg === 'object') {
        // HTMX returns strings, so convert it to an object
        let obj = JSON.parse(msg.xhr.responseText)
        msg = obj.message
    }

    toast.children[0].innerText = msg;
    if(err) {
        toast.classList.add('error')
    }
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show')
        toast.children[0].innerText = 'Loading...'
        if(err) {
            toast.classList.remove('error')
        }
    }, timeout)
}

// Listen for toast messaging from the server
htmx.on('showToast', evt => {
    console.log('got a toast')
    showToast(evt.detail.value)
})

window.showToast = showToast