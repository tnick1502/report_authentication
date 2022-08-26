function checkForm(username, password) {
	if (username === '' || password === '') {
		return false
	} else {
		return true
	}
}

function login(username, password, gotoUrl = null) {
	if (checkForm(username, password)) {
		try {
			fetch('../authorization/sign-in/', {
				method: 'POST', // *GET, POST, PUT, DELETE, etc.
				credentials: 'include', // include, *same-origin, omit
				headers: {
					Accept: 'application/json',
					'Content-Type': 'application/x-www-form-urlencoded',
					// 'Content-Type': 'application/x-www-form-urlencoded',
					'X-Requested-With': 'XMLHttpRequest',
				},
				body: `grant_type=password&username=${username}&password=${password}`,
			}).then(() => {
				if (gotoUrl) window.location.href = gotoUrl
				if (!gotoUrl) window.location.reload()
			})
		} catch (err) {
			console.error(`Error: ${err}`)
		}
	} else {
		alert('Заполните все поля')
	}
}

const form = document.getElementById('login-form')

if (form) {
	form.addEventListener('submit', function (event) {
		event.preventDefault()

		login(form.username.value, form.password.value)
	})
}

const btnOut = document.getElementById('btn-out')
if (btnOut) {
	btnOut.addEventListener('click', (event) => {
		event.preventDefault()
		fetch('../authorization/sign-out/', {
			method: 'GET', // *GET, POST, PUT, DELETE, etc.
			credentials: 'include', // include, *same-origin, omit
		}).then(() => {
			window.location.reload()
		})
	})
}

const btnTest = document.getElementById('btn-test')
if (btnTest) {
	btnTest.addEventListener('click', (event) => {
		event.preventDefault()
		login('trial', 'trial', '/login/')
	})
}
