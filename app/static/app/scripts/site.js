function draw_delimiter () {
    let canvas = document.getElementById('nav-delimiter')
    if (canvas){
        let h = canvas.height
        let ctx = canvas.getContext("2d")
        ctx.strokeStyle = getComputedStyle(canvas).getPropertyValue('--clr-text')
        ctx.lineWidth = 16
        ctx.moveTo(8 , h+1)
        ctx.lineTo(32, -1 )
        ctx.moveTo(32, h+1)
        ctx.lineTo(56, -1 )
        ctx.moveTo(56, h+1)
        ctx.lineTo(80, -1 )
        ctx.stroke()
    }
}

function switch_contact_display () {
    let checkbox = document.getElementById('id_email_allowed')
    let div = document.getElementById('div_contact')
    if (checkbox.checked) {
        div.style.display = ''
    }
    else {
        div.style.display = 'none'
    }
}

let carousel_content = []
let carousel_pos = 0
let carousel_hovered = false
let carousel_identifier = -1

function prepare_carousel () {
    let carousel = document.getElementById('carousel-content')
    if (carousel && carousel.children.length > 0) {
        carousel_content = []
        for (child of carousel.children) {
            carousel_content.push(child)
        }
        carousel_pos = 0

        for (let i = 0; i < carousel_content.length;  i++) {
            carousel_content[0].style.display = 'none'
        }

        carousel_content[0].style.display = 'inherit'

        carousel = document.getElementById('carousel')
        carousel.addEventListener('mouseenter', () => {carousel_hovered = true })
        carousel.addEventListener('mouseleave', () => {carousel_hovered = false})
        window.clearInterval(carousel_identifier)
        carousel_identifier = window.setInterval(() => {
            if (!carousel_hovered) carousel_right()
        }, 3500)
    }
}

function carousel_right () {
    next_pos = carousel_pos + 1
    if (next_pos >= carousel_content.length) next_pos = 0

    for (let i = 0; i < carousel_content.length;  i++) {
        carousel_content[i].setAttribute('class', '')
        carousel_content[i].style.display = 'none'
    }

    carousel_content[carousel_pos].setAttribute('class', 'anim_right_initial')
    carousel_content[next_pos    ].setAttribute('class', 'anim_right_new'    )
    carousel_content[carousel_pos].style.display = 'inherit'
    carousel_content[next_pos    ].style.display = 'inherit'

    carousel_pos = next_pos
}

function carousel_left () {
    next_pos = carousel_pos - 1
    if (next_pos < 0) next_pos = carousel_content.length-1

    for (let i = 0; i < carousel_content.length;  i++) {
        carousel_content[i].setAttribute('class', '')
        carousel_content[i].style.display = 'none'
    }

    carousel_content[carousel_pos].setAttribute('class', 'anim_left_initial')
    carousel_content[next_pos    ].setAttribute('class', 'anim_left_new'    )
    carousel_content[carousel_pos].style.display = 'inherit'
    carousel_content[next_pos    ].style.display = 'inherit'

    carousel_pos = next_pos
}

window.onload = function () {
    draw_delimiter()
    prepare_carousel()
}
