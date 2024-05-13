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

window.addEventListener('load', () => {
    document.getElementById('main').addEventListener('scroll', checkScroll)
    document.getElementById('manage-scroll-to-top').addEventListener('click', scrollToTop)
})
