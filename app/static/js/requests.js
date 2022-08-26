function checkForm(username, password) {
	if (username === '' || password === '') {
		return false
	} else {
		return true
	}
}

const form = document.getElementById('login-form')

form.addEventListener('submit', function (event) {
	event.preventDefault()

	let username = form.username.value
	let password = form.password.value

	console.log(username, password)

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
			})
				.then((response) => {
					// console.log('Completed!', response)
				})
				.then(() => {
					window.location.reload()
				})
		} catch (err) {
			console.error(`Error: ${err}`)
		}
	} else {
		alert('Заполните все поля')
	}
})
