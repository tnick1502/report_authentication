// ЗАПРОС ОТЧЕТА
window.addEventListener('load', function () {
	const requestReport = document.getElementById('request-report')
	if (requestReport) {
		const maxDataRows = 10
		const addRequestFormRow = () => {
			if (dataRows >= maxDataRows) return

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
		const deleteRequestFormRow = () => {
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
		const fillInputTable = (_data) => {
			const keys = Object.keys(_data)
			const dataLenth = keys.length

			while (dataRows < dataLenth && dataRows < maxDataRows) {
				addRequestFormRow()
			}

			if (dataRows < keys.length) return

			for (let row = 0; row < keys.length; row++) {
				let inputRow = document.getElementById(`inputParam_${row + 1}`)
				let inputRowVal = document.getElementById(`inputParam_${row + 1}_val`)

				if (!inputRow || !inputRowVal) continue

				inputRow.value = keys[row]
				inputRowVal.value = _data[keys[row]]
			}
		}
		const fillFormAfterSubmit = (_form) => {
			if (!_form) return

			const wasSubmitted = localStorage.getItem('wasSubmitted')
			if (!wasSubmitted) return

			const _objNum = localStorage.getItem('inputObj'),
				_labNum = localStorage.getItem('inputLabNo'),
				_testType = localStorage.getItem('inputType'),
				_tableData = JSON.parse(localStorage.getItem('inputData'))['data']

			if (!_objNum || !_labNum || !_testType) return

			const _inputObj = document.getElementById('inputObj'),
				_inputLabNo = document.getElementById('inputLabNo'),
				_inputType = document.getElementById('inputType')

			if (!_inputObj || !_inputLabNo || !_inputType) return

			_inputObj.value = _objNum
			_inputLabNo.value = _labNum
			_inputType.value = _testType

			const requestReportSuccses = document.getElementById(
				'request-report-succses'
			)
			if (requestReportSuccses) {
				requestReportSuccses.classList.add('request-report-succses-show')
			}

			fillInputTable(_tableData)

			// Загружаем куар код из памяти
			const QRString = localStorage.getItem('resultQR')
			const qrBLob = dataURItoBlob(QRString)
			if (qrBLob) {
				setTimeout(
					downloadData(qrBLob, `${_objNum} - ${_labNum} - ${_testType}`),
					0
				)
			}

			localStorage.removeItem('wasSubmitted')
			localStorage.removeItem('inputObj')
			localStorage.removeItem('inputLabNo')
			localStorage.removeItem('inputType')
			localStorage.removeItem('inputData')

			localStorage.removeItem('resultQR')
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

		inputObj.addEventListener('input', requiredChange)
		inputLabNo.addEventListener('input', requiredChange)
		inputType.addEventListener('input', requiredChange)

		// Заполняем данными форму, если страничка была обновлена из-за успешной ее отправки
		fillFormAfterSubmit(requestReport)
		requiredChange()

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
})

function sendRequestReport(info, tableData) {
	fetch('/reports/report_and_qr/', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({
			object_number: info['inputObj'],
			laboratory_number: info['inputLabNo'],
			test_type: info['inputType'],
			data: tableData,
			active: true,
		}),
	}).then((response) => {
		if (!response.ok) {
			// console.log(response)
			serverError()
		} else {
			response.blob().then((response_data) => {
				if (response_data) {
					// Показ сообщения об успехе
					const requestReportSuccses = document.getElementById(
						'request-report-succses'
					)
					if (requestReportSuccses) {
						requestReportSuccses.classList.add('request-report-succses-show')
					}

					// Скачивание кода
					// downloadData(
					// 	response_data,
					// 	`${info['inputObj']} - ${info['inputLabNo']} - ${info['inputType']}`
					// )

					localStorage.setItem('wasSubmitted', true)
					localStorage.setItem('inputObj', info['inputObj'])
					localStorage.setItem('inputLabNo', info['inputLabNo'])
					localStorage.setItem('inputType', info['inputType'])
					localStorage.setItem('inputData', JSON.stringify({ data: tableData }))

					const reader = new FileReader()

					reader.onload = (event) => {
						localStorage.setItem('resultQR', event.target.result)
					}

					reader.readAsDataURL(response_data)

					window.location.reload()
				} else {
					serverError()
				}
			})
			// window.location.reload()
		}
	})
}

function clearSubmit() {
	const inputs = document.querySelectorAll('#request-report .form-control')
	inputs.forEach((input) => {
		input.classList.remove('is-valid')
		input.classList.remove('is-invalid')
	})

	const requestReportSuccses = document.getElementById('request-report-succses')
	if (requestReportSuccses) {
		requestReportSuccses.classList.remove('request-report-succses-show')
	}
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

function requiredChange() {
	const _inputObj = document.getElementById('inputObj'),
		_inputLabNo = document.getElementById('inputLabNo'),
		_inputType = document.getElementById('inputType')

	if (
		_inputObj.value.length > 0 &&
		_inputLabNo.value.length > 0 &&
		_inputType.value.length > 0
	) {
		document.getElementById('request-report-submit-btn').disabled = false
	} else {
		document.getElementById('request-report-submit-btn').disabled = true
	}
}
// ===================== ПРОЧИЕ ФУКНЦИИ =====================
function downloadData(_BLOB, _file_name) {
	const a = document.createElement('a')
	a.href = window.URL.createObjectURL(_BLOB)
	a.target = '_blank'
	a.download = _file_name
	a.click()
}

function dataURItoBlob(dataURI) {
	// convert base64 to raw binary data held in a string
	var byteString = atob(dataURI.split(',')[1])

	// separate out the mime component
	var mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0]

	// write the bytes of the string to an ArrayBuffer
	var arrayBuffer = new ArrayBuffer(byteString.length)
	var _ia = new Uint8Array(arrayBuffer)
	for (var i = 0; i < byteString.length; i++) {
		_ia[i] = byteString.charCodeAt(i)
	}

	var dataView = new DataView(arrayBuffer)
	var blob = new Blob([dataView], { type: mimeString })
	return blob
}
