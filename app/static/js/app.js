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

			closeNav()

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

// console.log(toast)

const toastBtnAccept = document.getElementById('btnAccept')

function setCookie(name, value, days) {
	var expires = ''
	if (days) {
		var date = new Date()
		date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000)
		expires = '; expires=' + date.toUTCString()
	}
	document.cookie = name + '=' + (value || '') + expires + '; path=/'
}
function getCookie(name) {
	var nameEQ = name + '='
	var ca = document.cookie.split(';')
	for (var i = 0; i < ca.length; i++) {
		var c = ca[i]
		while (c.charAt(0) == ' ') c = c.substring(1, c.length)
		if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length)
	}
	return null
}

function eraseCookie(name) {
	document.cookie = name + '=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;'
}

function cookieConsent() {
	if (!getCookie('allowCookies')) {
		toast.show()
	}
}

toastBtnAccept.addEventListener('click', (event) => {
	setCookie('allowCookies', '1', 7)
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


// ===================== СТАТИСТИКА ПРОТОКОЛОВ =====================
const reportsCounter = document.getElementById('reportsCounter')
if (reportsCounter) {
	fetch(' ../reports/count', {
		method: 'GET', // *GET, POST, PUT, DELETE, etc.
		//credentials: 'include', // include, *same-origin, omit
	}).then((response) => {
		if (!response.ok) {
			return
		}
		response.json().then((data) => {
			if (typeof data != 'undefined') {
				reportsCounter.innerText = `${data}`
				}
			})
		})
}

// ===================== РАБОТА С ОТЧЕТАМИ =====================

// УДАЛЕНИЕ ОТЧЕТА
const deleteReportBtns = document.querySelectorAll(
	'.delete-report-btn[data-id]'
)

if (deleteReportBtns.length > 0) {
	let delReportId = null
	let delReportDialog = document.getElementById('del-report-dialog')

	deleteReportBtns.forEach((item) => {
		item.addEventListener('click', (event) => {
			event.preventDefault()
			if (!delReportDialog) return

			delReportDialog.classList.add('del-report-modal__wrapper_show')

			const delItem = event.currentTarget
			delReportId = delItem.dataset.id
		})
	})

	const delReport__btnCancel = document.getElementById('del-report__btn-cancel')

	delReport__btnCancel.addEventListener('click', (event) => {
		event.preventDefault()
		event.stopPropagation()

		delReportId = null
		delReportDialog.classList.remove('del-report-modal__wrapper_show')
	})

	document
		.getElementById('del-report__btn-del')
		.addEventListener('click', (event) => {
			event.preventDefault()
			event.stopPropagation()

			if (!delReportId) return

			fetch(`../reports/${delReportId}`, {
				method: 'DELETE', // *GET, POST, PUT, DELETE, etc.
			}).then(() => {
				// console.log(delReportId)
				delReportDialog.classList.remove('del-report-modal__wrapper_show')

				window.location.reload()
			})
		})
}

// СКАЧИВАНИЕ ОТЧЕТА
const downloadReportBtns = document.querySelectorAll(
	'.download-report-btn[data-id]'
)

if (downloadReportBtns.length > 0) {
	let downlReportId = null

	downloadReportBtns.forEach((item) => {
		item.addEventListener('click', (event) => {
			{
				event.preventDefault()

				const downlItem = event.currentTarget
				downlReportId = downlItem.dataset.id
				const _inputObj = downlItem.dataset.object_number
				const _inputLabNo = downlItem.dataset.laboratory_number
				const _inputType = downlItem.dataset.test_type

				if (!downlReportId) return

				// console.log(downlReportId)
				fetch(`../reports/qr?id=${downlReportId}`, {
					method: 'POST',
				})
					.then((response) => {
						return response.blob()
					})
					.then((data) => {
						downloadData(data, `${_inputObj} - ${_inputLabNo} - ${_inputType}`)
					})
			}
		})
	})
}

// ОБНОВЛЕНИЕ ОТЧЕТА
const updateReportBtns = document.querySelectorAll(
	'.update-report-btn[data-id]'
)

if (updateReportBtns.length > 0) {
	updateReportBtns.forEach((item) => {
		item.addEventListener('click', onUpdateReportClick)
	})

	function onUpdateReportClick(event) {
		event.preventDefault()

		const _requestReport = document.getElementById('request-report'),
			_inputObj = document.getElementById('inputObj'),
			_inputLabNo = document.getElementById('inputLabNo'),
			_inputType = document.getElementById('inputType')

		if (_requestReport && _inputObj && _inputLabNo && _inputType) {
			_inputObj.value = event.currentTarget.dataset.object_number
			_inputLabNo.value = event.currentTarget.dataset.laboratory_number
			_inputType.value = event.currentTarget.dataset.test_type
		}

		const gotoBlockValue =
			_requestReport.parentNode.getBoundingClientRect().top +
			pageYOffset -
			document.querySelector('header').offsetHeight
		window.scrollTo({
			top: gotoBlockValue,
			behavior: 'smooth',
		})

		requiredChange()
	}
}


// ПОЛУЧЕНИЕ ТОКЕНА
const getTokenBtn = document.getElementById('get-token-btn')
const requestTokenDialog = document.getElementById('request-token-dialog')
const requestTokenDialogBtn = document.getElementById('request-token-dialog-btn')

if (getTokenBtn) {
	getTokenBtn.addEventListener('click', ()=>{
		// console.log(getTokenBtn);
		fetch('../authorization/token/', {
			method: 'POST', // *GET, POST, PUT, DELETE, etc.
			credentials: 'include', // include, *same-origin, omit
		}).then((response) => {
			if (!response.ok) {
				console.log(response);
				requestTokenDialog.classList.add('request-token-modal__wrapper_show')
			}
			else {
				response.json().then((data)=>{
					// console.log(data['access_token']);
					const content = document.getElementById('request-token__content')
					content.innerText = 'Токен скопирован в буфер обмена'
					navigator.clipboard.writeText(data['access_token'])
					requestTokenDialog.classList.add('request-token-modal__wrapper_show')
				})
			}
		})
	})
}
if (requestTokenDialogBtn) {
	requestTokenDialogBtn.addEventListener('click', ()=>{
		requestTokenDialog.classList.remove('request-token-modal__wrapper_show')
	})
}

// ===================== НАВИГЦИЯ В ЛИЧНОМ КАБИНЕТЕ =====================
const navItemsPersonal = document.querySelectorAll(
	'.nav-link-personal[data-goto]'
)
if (navItemsPersonal.length > 0) {
	navItemsPersonal.forEach((item) => {
		item.addEventListener('click', onNavItemPersonalClick)
	})

	function onNavItemPersonalClick(event) {
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

			closeNavPersonal()

			event.preventDefault()
		}
	}
}

const navMenuPersonal = document.getElementById('navbar-collapse-personal'),
	navTogglePersonal = document.getElementById('nav-toggle-personal'),
	navClosePersonal = document.getElementById('nav-close-personal'),
	navWrapperPersonal = document.getElementById(
		'navbar-collapse-wrapper-personal'
	)

if (navTogglePersonal) {
	navTogglePersonal.addEventListener('click', () => {
		navWrapperPersonal.classList.add('navbar-collapse-wrapper-show')
		navMenuPersonal.classList.add('navbar-collapse-show')
		body.classList.add('body-hidden')
	})
}

function closeNavPersonal() {
	navMenuPersonal.classList.remove('navbar-collapse-show')
	body.classList.remove('body-hidden')
	navWrapperPersonal.classList.remove('navbar-collapse-wrapper-show')
}

if (navClosePersonal) {
	navClosePersonal.addEventListener('click', closeNavPersonal)
}
