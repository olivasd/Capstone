function checkReCAPTCHA(){
	var captcha = document.getElementById('captchamsg');
	captcha.style.visibility='hidden';
	
	if(grecaptcha.getResponse().length === 0) {
		captcha.style.visibility='visible';
		event.preventDefault();
	}
}