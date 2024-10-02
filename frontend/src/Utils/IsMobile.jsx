export default function IsMobile() {
	function Android() {
		return navigator.userAgent.match(/Android/i)
	}
	function BlackBerry() {
		return navigator.userAgent.match(/BlackBerry/i)
	}
	function iOS() {
		return navigator.userAgent.match(/iPhone|iPad|iPod/i)
	}
	function Opera() {
		return navigator.userAgent.match(/Opera Mini/i)
	}
	function Windows() {
		return navigator.userAgent.match(/IEMobile/i)
	}
	function Any() {
		return Android() || BlackBerry() || iOS() || Opera() || Windows()
	}

	return Any()
}
