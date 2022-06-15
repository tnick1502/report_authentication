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

// ===================== ИНИЦИАЛИЗАЦИЯ КАРУСЕЛЬКИ =====================
let swiperDevices = new Swiper('.devices__container', {
	loop: true,
	slidesPerView: 'auto',
	centeredSlides: true,
	grabCursor: true,
	autoplay: {
		delay: 3500,
		disableOnInteraction: false,
	},
	pagination: {
		el: '.swiper-pagination',
		dynamicBullets: true,
		clickable: true,
	},
})
