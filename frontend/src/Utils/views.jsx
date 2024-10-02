export function parseViews(data) {
	const options = { year: 'numeric', month: 'short', day: 'numeric' }

	const views = []
	const dates = []

	const items = Object.keys(data)

	let lastDate = null

	if (items.length > 0) {
		items.forEach((item) => {
			views.push(data[item])
			lastDate = new Date(item)
			const date = new Intl.DateTimeFormat('ru-RU', options)
				.format(new Date(item))
				.replace(' г.', '')

			dates.push(date)
		})

		const currentDate = new Date()
		if (currentDate.getMonth() > lastDate.getMonth()) {
			views.push(0)
			dates.push(
				new Intl.DateTimeFormat('ru-RU', options)
					.format(currentDate)
					.replace(' г.', '')
			)
		}
		const resultData = { views: views, dates: dates }
		return resultData
	}

	return { views: [], dates: [] }
}

export async function getViews() {
	const range = 300
	return     {
        '2024-05-01': Math.round(Math.random() * range),
        '2024-06-01': Math.round(Math.random() * range),
        '2024-07-01': Math.round(Math.random() * range),
        '2024-08-01': Math.round(Math.random() * range),
        '2024-09-01': Math.round(Math.random() * range),
        '2024-10-01': Math.round(Math.random() * range),
        '2024-11-01': Math.round(Math.random() * range)
    }
}