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


function assign (elem, callback) {
    try {
        if (typeof elem === 'string') elem = document.getElementById(elem)
        elem.addEventListener('click', callback)
    }
    catch {}
}


function scrollToTop () {
    document.getElementById('main').scrollTo({behavior: 'smooth', top: 0});
}

function checkScroll () {
    const scrollToTopElem = document.getElementById('manage-scroll-to-top');

    if (document.getElementById('main').scrollTop > 0) {
        scrollToTopElem.classList.add('shown')
    } else {
        scrollToTopElem.classList.remove('shown')
    }
}


function create_status_item (statusname) {
    const statuscontent = STATUSES[statusname]

    const button = document.createElement('button')
    button.setAttribute('type', 'button')
    button.dataset.orderstatus = statusname
    button.classList.add('order-status-button')
    button.style.background = statuscontent.colour
    button.innerText = statuscontent.title

    if (orderstatus !== statusname) button.classList.add('other')
  
    assign(button, () => { orderstatus = statusname; update_status_dialog(orderid) })
  
    return button
}

function update_status_dialog (id) {
    let dialog = document.getElementById('order-dialog')
    dialog.ariaBusy = 'true'

    let order = orders.find(o => o.id == id)
    let comment_elem = document.getElementById('order-dialog-comment')

    comment_elem.value = order.comment
    comment_elem.addEventListener('input', (event) => { order.comment = event.target.value })

    const items = document.getElementById('order-dialog-statuses')
    items.innerHTML = ''
    for (const name of Object.keys(STATUSES)) items.appendChild(create_status_item(name))

    dialog.ariaBusy = 'false'
}

function open_status_dialog (id, status) {
    let dialog = document.getElementById('order-dialog')

    orderid = id
    orderstatus = status

    update_status_dialog(id)
    
    assign('order-dialog-save', () => {
        let elem = document.getElementById('order-status-' + orderid)
        elem.innerText = STATUSES[orderstatus].title
        elem.style.background = STATUSES[orderstatus].colour

        fetch('/update/order/' + orderid, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': readCookie('csrftoken')
            },
            body: JSON.stringify({
                status: orderstatus,
                comment: document.getElementById('order-dialog-comment').value
            })
        })
    })

    dialog.ariaModal = 'true'
    dialog.showModal()
}

function close_status () {
    let dialog = document.getElementById('order-dialog')
    dialog.close()
}

function on_close_dialog () {
    let dialog = document.getElementById('order-dialog')
    dialog.ariaModal = 'false'
}


window.onload = function() {
    document.getElementById('main').addEventListener('scroll', checkScroll)
    document.getElementById('manage-scroll-to-top').addEventListener('click', scrollToTop)

    const elements = Object.values(document.getElementsByClassName('status-dialog-button'))
    
    elements.forEach(element => {
        element.addEventListener('click', () => {
            open_status_dialog(element.dataset.orderid, element.dataset.orderstatus)
        })
    })

    assign('order-dialog-close', close_status)
    assign('order-dialog-dark', close_status)

    try { document.getElementById('cart-dialog').addEventListener('close', on_close_dialog) } catch {}
}
