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

function setCookie (name, value, days) {
    var expires = ""
    if (days) {
        var date = new Date()
        date.setTime(date.getTime() + (days*24*60*60*1000))
        expires = "; expires=" + date.toUTCString()
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/"
}

function deleteCookie (name) {
    setCookie(name, "", -1)
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
    const scrollToTopElem = document.getElementById('store-scroll-to-top');

    if (document.getElementById('main').scrollTop > 0) {
        scrollToTopElem.classList.add('shown')
    } else {
        scrollToTopElem.classList.remove('shown')
    }
}


function get_cart () {
    let rawCart = (readCookie('cart') || '').split('/').slice(0, -1);
    let cart = {}
    for (let i = 0; i < rawCart.length; i++) {
        let item = rawCart[i].split(':')
        cart[item[0]] = parseInt(item[1])
    }
    return cart
}

function process_cart () {
    let cart = get_cart()
    let cart_block = document.getElementById('cart')
    let outputs = document.getElementById('cart-total')

    let total = 0
    let total_sum = 0

    for (const [key, value] of Object.entries(cart)) {
        total += value
        total_sum += value * parseInt(PRODUCTS[key].price)
    }

    if (total) cart_block.classList.add('shown')
    else cart_block.classList.remove('shown')

    outputs.children[0].innerText = `${total} в корзине`
    outputs.children[1].innerText = `${total_sum} ₽`

    outputs.children[0].setAttribute('value', total)
    outputs.children[1].setAttribute('value', total_sum)
}


function create_svg (path) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
    svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
    svg.setAttribute('viewBox', '0 -960 960 960')
    svg.setAttribute('width', '30')
    svg.setAttribute('height', '30')
    const path_elem = document.createElementNS('http://www.w3.org/2000/svg', 'path')
    path_elem.setAttribute('d', path)
    svg.appendChild(path_elem)
    return svg
}

function create_cart_item (product_id, quanity) {
    const div = document.createElement('section')
    div.classList.add('cart-dialog-item')
  
    const figure = document.createElement('figure')
    const img = document.createElement('img')
    img.src = PRODUCTS[product_id].image
    img.alt = PRODUCTS[product_id].name
    figure.appendChild(img)
    div.appendChild(figure)
  
    const itemInfo = document.createElement('div')
    const h2 = document.createElement('h2')
    h2.innerText = PRODUCTS[product_id].name
    itemInfo.appendChild(h2)
  
    const math = document.createElement('math')
    const mrow = document.createElement('mrow')
  
    const mi1 = document.createElement('mi')
    mi1.textContent = quanity
    mrow.appendChild(mi1)
  
    const mo1 = document.createElement('mo')
    mo1.textContent = '*'
    mrow.appendChild(mo1)
  
    const mi2 = document.createElement('mi')
    mi2.textContent = PRODUCTS[product_id].price + ' ₽'
    mrow.appendChild(mi2)
  
    const mo2 = document.createElement('mo')
    mo2.textContent = '='
    mrow.appendChild(mo2)
  
    const mi3 = document.createElement('mi')
    mi3.textContent = quanity * parseInt(PRODUCTS[product_id].price) + ' ₽'
    mrow.appendChild(mi3)
  
    math.appendChild(mrow)
    itemInfo.appendChild(math)
    div.appendChild(itemInfo)
  
    const menu = document.createElement('menu')
  
    if (PRODUCTS[product_id].type === 'accessory') {
        const li1 = document.createElement('li')
        const button1 = document.createElement('button')
        button1.type = 'button'
        button1.title = 'убрать одну копию'
        button1.appendChild(create_svg('M200-446.667v-66.666h560v66.666H200Z'))
        assign(button1, () => {
            setCookie('cart', (readCookie('cart') || '').replace(
                RegExp(product_id + ':\\d+/', 'i'),
                quanity === 1 ? '' : `${product_id}:${quanity - 1}/`
            ), 14)
            if (quanity === 1) {
                document.querySelector(`[data-item="${product_id}"]`).classList.remove('added')
            }
            update_cart()
        })
        li1.appendChild(button1)
        menu.appendChild(li1)
    
        const li2 = document.createElement('li')
        const button2 = document.createElement('button')
        button2.type = 'button'
        button2.title = 'добавить одну копию'
        button2.appendChild(create_svg('M446.667-446.667H200v-66.666h246.667V-760h66.666v246.667H760v66.666H513.333V-200h-66.666v-246.667Z'))
        assign(button2, () => {
            setCookie('cart', (readCookie('cart') || '').replace(
                RegExp(product_id + ':\\d+/', 'i'),
                `${product_id}:${quanity + 1}/`
            ), 14)
            update_cart()
        })
        li2.appendChild(button2)
        menu.appendChild(li2)
    }

    else {
        const li = document.createElement('li')
        const button = document.createElement('button')
        button.type = 'button'
        button.title = 'убрать из корзины'
        button.appendChild(create_svg('m251.333-204.667-46.666-46.666L433.334-480 204.667-708.667l46.666-46.666L480-526.666l228.667-228.667 46.666 46.666L526.666-480l228.667 228.667-46.666 46.666L480-433.334 251.333-204.667Z'))
        assign(button, () => {
            setCookie('cart', (readCookie('cart') || '').replace(
                RegExp(product_id + ':\\d+/', 'i'),
                ''
            ), 14)
            document.querySelector(`[data-item="${product_id}"]`).classList.remove('added')
            update_cart()
        })
        li.appendChild(button)
        menu.appendChild(li)
    }
  
    div.appendChild(menu)
  
    return div
}

function update_cart () {
    let dialog = document.getElementById('cart-dialog')
    dialog.ariaBusy = 'true'

    let cart = get_cart()

    let total_sum = 0
    for (const [key, value] of Object.entries(cart)) total_sum += value * parseInt(PRODUCTS[key].price)

    document.getElementById('cart-dialog-sum').innerText = `${total_sum} ₽`

    if (Object.keys(cart).find(k => k.startsWith('a'))) {
        document.getElementById('cart-dialog-address').removeAttribute('disabled')
    }
    else {
        document.getElementById('cart-dialog-address').setAttribute('disabled', 'disabled')
    }

    const items = document.getElementById('cart-dialog-items')
    items.innerHTML = ''
    for (const [key, value] of Object.entries(cart)) items.appendChild(create_cart_item(key, value))

    process_cart()
    dialog.ariaBusy = 'false'
}

function deploy_cart () {
    let dialog = document.getElementById('cart-dialog')

    update_cart()

    dialog.ariaModal = 'true'
    dialog.showModal()
}

function close_cart () {
    let dialog = document.getElementById('cart-dialog')
    dialog.close()
}

function on_close_dialog () {
    let dialog = document.getElementById('cart-dialog')
    dialog.ariaModal = 'false'
}

function clear_cart () {
    setCookie('cart', '', -1)
    const elements = Object.values(document.getElementsByClassName('store-price-block'))
    elements.forEach(e => { e.classList.remove('added') })
    process_cart()
}

async function order_cart () {
    let address = document.getElementById('cart-dialog-address')
    if (!address.disabled && !address.value) return alert('Вам необходимо указать адрес доставки')

    let cart = get_cart()
    if (!Object.keys(cart).length) return alert('Выберите что-нибудь для оформления заказа')

    fetch('/place/order/', {
        method: 'POST',
        headers: {
            'content-type': 'text/plain',
            'X-CSRFToken': readCookie('csrftoken')
        },
        body: JSON.stringify({
            address: address.value,
            cart: cart,
            csrfmiddlewaretoken: csrftoken
        }),
    })

    close_cart()
    document.getElementById('thanks-dialog').showModal()

    clear_cart()
}


window.onload = function() {
    document.getElementById('main').addEventListener('scroll', checkScroll)
    document.getElementById('store-scroll-to-top').addEventListener('click', scrollToTop)

    const elements = Object.values(document.getElementsByClassName('store-price-block'))
    
    elements.forEach(element => {
        element.querySelector(':scope > .store-buy')?.addEventListener('click', function() {
            if (element.classList.contains('added')) return

            element.classList.add('added')
            setCookie('cart', (readCookie('cart') || '') + element.dataset.item + ':1/', 14)
            process_cart()
        })

        element.querySelector(':scope > .store-cancel')?.addEventListener('click', function() {
            if (!element.classList.contains('added')) return

            element.classList.remove('added')
            setCookie('cart', (readCookie('cart') || '').replace(RegExp(element.dataset.item + ':\\d+/', 'i'), ''), 14)
            process_cart()
        })

        if (element.dataset.item in get_cart()) element.classList.add('added')
    })

    const cart_block = document.getElementById('cart')

    assign('cart-open', () => {
        if (window.matchMedia('screen and (max-width: 650px)').matches) {
            try { deploy_cart() }
            catch { window.location.href = '/auth/sign-in/' }
        }
        else cart_block.classList.toggle('minimized')
    })
    assign('cart-continue', deploy_cart)
    assign('cart-cancel', clear_cart)
    assign('cart-dialog-dark', close_cart)
    assign('cart-dialog-cancel', () => { clear_cart(); update_cart() })
    assign('cart-dialog-close', close_cart)
    assign('cart-dialog-order', order_cart)

    assign('thanks-dialog-dark', () => { document.getElementById('thanks-dialog').close() })
    assign('thanks-dialog-close', () => { document.getElementById('thanks-dialog').close() })

    try { document.getElementById('cart-dialog').addEventListener('close', on_close_dialog) } catch {}

    process_cart()
}
