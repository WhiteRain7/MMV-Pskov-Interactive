window.onload = function() {
    document.getElementById('main').addEventListener('scroll', checkScroll);
    document.getElementById('store-scroll-to-top').addEventListener('click', scrollToTop);

    Object.values(document.getElementsByClassName('store-buy')).forEach(element => {
        element.addEventListener('click', function() {
            this.parentElement.classList.add('added');
        })
    });
    Object.values(document.getElementsByClassName('store-cancel')).forEach(element => {
        element.addEventListener('click', function() {
            this.parentElement.classList.remove('added');
        })
    });
}

function scrollToTop () {
    document.getElementById('main').scrollTo({behavior: 'smooth', top: 0});
}

function checkScroll () {
    const scrollToTopElem = document.getElementById('store-scroll-to-top');

    if (document.getElementById('main').scrollTop > 0) {
        scrollToTopElem.classList.add('shown');
    } else {
        scrollToTopElem.classList.remove('shown');
    }
}
