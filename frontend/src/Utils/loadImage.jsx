export function loadImage(url) {
	return new Promise((resolve, reject) => {
		const loadImg = new Image()
		loadImg.src = url
		loadImg.onload = () => resolve(url)

		loadImg.onerror = (err) => reject(err)
	})
}
