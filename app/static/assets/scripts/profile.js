function readCookie (name) {
    var nameEQ = name + "="
    var ca = document.cookie.split(';')
    for(var i=0;i < ca.length;i++) {
        var c = ca[i]
        while (c.charAt(0)==' ') c = c.substring(1,c.length)
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length)
    }
    return null
}


window.onload = function() {
    const input = document.getElementById("profile-image-input")

    if (input) input.addEventListener("change", function() {
        const reader = new FileReader()
        reader.addEventListener("load", () => {
            document.getElementById("profile-content-image").src = reader.result
        })
        reader.readAsDataURL(this.files[0])

        const body = new FormData()
        body.append("photo", this.files[0])

        fetch("/edit/profile/", {
            method: "POST",
            headers: {
                "X-CSRFToken": readCookie("csrftoken")
            },
            body
        })
    })
}
