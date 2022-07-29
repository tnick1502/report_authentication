// ===================== NAVIGATION =====================
const navItems = document.querySelectorAll('.nav-link[data-goto]')
if (navItems.length > 0) {
	navItems.forEach((item) => {
		item.addEventListener('click', onNavItemClick)
	})

	function onNavItemClick(event) {
		const navItem = event.target
		if (navItem.dataset.goto && document.getElementById(navItem.dataset.goto)) {
			const gotoBlock = document.getElementById(navItem.dataset.goto)
			const gotoBlockValue =
				gotoBlock.getBoundingClientRect().top +
				pageYOffset -
				document.querySelector('header').offsetHeight
			window.scrollTo({
				top: gotoBlockValue,
				behavior: 'smooth',
			})
			event.preventDefault()
		}
	}
}

// ===================== ОТКРЫТИЕ ЗАКРЫТИЕ НАВИГАЦИИ =====================
const navMenu = document.getElementById('navbar-collapse'),
	navToggle = document.getElementById('nav-toggle'),
	navClose = document.getElementById('nav-close'),
	body = document.getElementById('body'),
	navWrapper = document.getElementById('navbar-collapse-wrapper')

if (navToggle) {
	navToggle.addEventListener('click', () => {
		navWrapper.classList.add('navbar-collapse-wrapper-show')
		navMenu.classList.add('navbar-collapse-show')
		body.classList.add('body-hidden')
	})
}

function closeNav() {
	navMenu.classList.remove('navbar-collapse-show')
	body.classList.remove('body-hidden')
	navWrapper.classList.remove('navbar-collapse-wrapper-show')
}

if (navClose) {
	navClose.addEventListener('click', closeNav)
}

// ===================== ПРОВЕРИТЬ НА МОБИЛЬНУЮ ВЕРСИЮ ОЧЕНЬ ПРОСТО =====================

isMobile = {
	Android: function () {
		return navigator.userAgent.match(/Android/i)
	},
	BlackBerry: function () {
		return navigator.userAgent.match(/BlackBerry/i)
	},
	iOS: function () {
		return navigator.userAgent.match(/iPhone|iPad|iPod/i)
	},
	Opera: function () {
		return navigator.userAgent.match(/Opera Mini/i)
	},
	Windows: function () {
		return navigator.userAgent.match(/IEMobile/i)
	},
	any: function () {
		return (
			isMobile.Android() ||
			isMobile.BlackBerry() ||
			isMobile.iOS() ||
			isMobile.Opera() ||
			isMobile.Windows()
		)
	},
}

// ===================== ОБРАБОТКА ОСНОВНОЙ КАРТИНКИ =====================

const homeImgLink = document.getElementById('homeImg')
const screenWidth = window.innerWidth

if (isMobile.any() && homeImgLink) {
	homeImgLink.addEventListener('click', (event) => {
		homeImgLink.classList.add('onscroll')
	})
}

if (isMobile.any() && homeImgLink) {
	const sectionTop =
		homeImgLink.offsetTop - (1 * document.documentElement.clientHeight) / 3
	window.addEventListener('scroll', () => {
		if (this.scrollY > sectionTop) {
			homeImgLink.classList.add('onscroll')
		} else {
			homeImgLink.classList.remove('onscroll')
		}
	})
}

// ===================== КУКИ ФАЙЛЫ =====================
const toastItem = document.getElementById('toast')
const toast = new bootstrap.Toast(toastItem)

console.log(toast)

const toastBtnAccept = document.getElementById('btnAccept')

function setCookie(name,value,days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}
function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}

function eraseCookie(name) {
    document.cookie = name +'=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
}

function cookieConsent() {
    if (!getCookie('allowCookies')) {
        toast.show()
    }
}

toastBtnAccept.addEventListener('click', (event)=>{
    setCookie('allowCookies','1',7)
    toast.hide()
})

// load
cookieConsent()

// for demo / testing only
//$('#btnReset').click(()=>{
//    // clear cookie to show toast after acceptance
//    eraseCookie('allowCookies')
//    toast.toast('show')
//})

