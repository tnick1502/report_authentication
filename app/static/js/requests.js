function checkForm(username, password) {
	if (username === '' || password === '') {
		return false
	} else {
		return true
	}
}

const form = document.getElementById('login-form')

form.addEventListener('submit', async function (event) {
	let username = form.username.value
	let password = form.password.value

	if (checkForm(username, password)) {
		try {
			let response = await fetch('/authorization/sign_in', {
				method: 'POST', // *GET, POST, PUT, DELETE, etc.
				mode: 'cors', // no-cors, *cors, same-origin
				cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
				credentials: 'same-origin', // include, *same-origin, omit
				headers: {
					'Content-Type': 'application/json',
					// 'Content-Type': 'application/x-www-form-urlencoded',
				},
				redirect: 'follow', // manual, *follow, error
				referrerPolicy: 'no-referrer', // no-referrer, *client
				body: {
					username: username,
					password: password,
					grant_type: 'password',
					scope: '',
					client_id: '',
					client_secret: '',
				},
			})
			console.log('Completed!', response)
		} catch (err) {
			console.error(`Error: ${err}`)
		}
	} else {
		alert('Заполните все поля')
	}

	//event.preventDefault()
})
