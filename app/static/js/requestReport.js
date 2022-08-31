// ЗАПРОС ОТЧЕТА
const requestReport = document.getElementById('request-report')
if (requestReport) {
	function addRequestFormRow() {
		if (dataRows >= 10) return

		const lastRow = document.getElementById(
			`inputParam_${dataRows}_val`
		).parentNode

		if (!lastRow) return

		dataRows = dataRows + 1

		const newRow = `
		<div class="form-group col-6">
		<input
			type="text"
			class="form-control"
			id="inputParam_${dataRows}"
			name="inputParam_${dataRows}"
			placeholder=""
			aria-describedby="validationFeedback"
			/>
			<div class="invalid-feedback" id="validationFeedback">
			Пожалуйста, заполните это поле.
		</div>
			</div>
			<div class="form-group col-6">
			<input
				type="text"
				class="form-control"
				id="inputParam_${dataRows}_val"
				name="inputParam_${dataRows}"
				placeholder=""
				aria-describedby="validationFeedback"
				/>
				<div class="invalid-feedback" id="validationFeedback">
				Пожалуйста, заполните это поле.
			</div>
				</div>`

		lastRow.insertAdjacentHTML('afterend', newRow)
	}
	function deleteRequestFormRow() {
		if (dataRows <= 3) return

		let lastRow = document.getElementById(
			`inputParam_${dataRows}_val`
		).parentNode

		if (!lastRow) return
		lastRow.parentNode.removeChild(lastRow)

		lastRow = document.getElementById(`inputParam_${dataRows}`).parentNode

		if (!lastRow) return
		lastRow.parentNode.removeChild(lastRow)

		dataRows = dataRows - 1
	}

	const requestFormAddBtn = document.getElementById('request-form-add-btn')
	const requestFormDeleteBtn = document.getElementById(
		'request-form-delete-btn'
	)

	let dataRows = 3

	if (requestFormAddBtn && requestFormDeleteBtn) {
		requestFormAddBtn.addEventListener('click', addRequestFormRow)
		requestFormDeleteBtn.addEventListener('click', deleteRequestFormRow)
	}

	// Включение выключение кнопки
	const inputObj = document.getElementById('inputObj'),
		inputLabNo = document.getElementById('inputLabNo'),
		inputType = document.getElementById('inputType')

	function requiredChange() {
		if (
			inputObj.value.length > 0 &&
			inputLabNo.value.length > 0 &&
			inputType.value.length > 0
		) {
			document.getElementById('request-report-submit-btn').disabled = false
		} else {
			document.getElementById('request-report-submit-btn').disabled = true
		}
	}

	inputObj.addEventListener('input', requiredChange)
	inputLabNo.addEventListener('input', requiredChange)
	inputType.addEventListener('input', requiredChange)

	//

	// Подкючением отправку формы
	requestReport.addEventListener('submit', (event) => {
		event.preventDefault()
		event.stopPropagation()

		// Очистка уже наложенных стилей проверки
		clearSubmit()

		let notValid = false
		// Проверяем обязательные поля
		if (inputObj.value.length === 0) {
			inputObj.classList.add('is-invalid')
			notValid = true
		} else inputObj.classList.add('is-valid')

		if (inputLabNo.value.length === 0) {
			inputLabNo.classList.add('is-invalid')
			notValid = true
		} else inputLabNo.classList.add('is-valid')

		if (inputType.value.length === 0) {
			inputType.classList.add('is-invalid')
			notValid = true
		} else inputType.classList.add('is-valid')

		// Проверяем парные поля (поля должны быть заполнены по парам)
		const inputs = document.querySelectorAll(
			'#request-report .col-6 .form-control'
		)
		// Будем проверять элементы парами, проходя по массиву через одного
		for (let i = 0; i < inputs.length - 1; i = i + 2) {
			// Пустые пары тупо пропускаем
			if (inputs[i].value.length === 0 && inputs[i + 1].value.length === 0) {
				continue
			}
			if (inputs[i].value.length === 0 && inputs[i + 1].value.length !== 0) {
				inputs[i].classList.add('is-invalid')
				inputs[i + 1].classList.add('is-valid')
        notValid = true
				continue
			}
			if (inputs[i].value.length !== 0 && inputs[i + 1].value.length === 0) {
				inputs[i].classList.add('is-valid')
				inputs[i + 1].classList.add('is-invalid')
        notValid = true
				continue
			}
			inputs[i].classList.add('is-valid')
			inputs[i + 1].classList.add('is-valid')
		}

		if (notValid) return

		// Содаем из формы класс с данными
		const formData = new FormData(event.target)

		const resultInfo = {}
		const resultData = {}

		for (var [key, value] of formData.entries()) {
			// Оба значения будут браться по параметру name парных элементов
			// Если name импута содержит нижнее подчеркивание, то это парный элемент
			if (key.includes('_')) {
				const data = formData.getAll(key)

				if (data[0].length === 0 || data[1].length === 0) {
					continue
				}

				resultData[data[0]] = data[1]
			} else {
				resultInfo[key] = value
			}
		}

		sendRequestReport(resultInfo, resultData)

		// requestReport.classList.add('was-validated')
	})
}

function sendRequestReport(info, data) {
	fetch('../reports/', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({
			object_number: info['inputObj'],
			laboratory_number: info['inputLabNo'],
			test_type: info['inputType'],
			data: data,
			active: true,
		}),
	}).then((response) => {
		console.log(response)
		if (!response.ok) {
			console.log('error')
			serverError()
		}
	})
}

function clearSubmit() {
	const inputs = document.querySelectorAll('#request-report .form-control')
	inputs.forEach((input) => {
		input.classList.remove('is-valid')
		input.classList.remove('is-invalid')
	})
}

function serverError() {
	const inputs = document.querySelectorAll(
		'#request-report .col-md-4 .form-control'
	)
	inputs.forEach((input) => {
		input.classList.remove('is-valid')
		input.classList.add('is-invalid')
	})
}
