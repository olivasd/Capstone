function blurConfirmPW() {
	document.getElementById('cfpassword_msg').style.visibility='hidden';
	checkPasswordsMatch();
}

function focusPassword() { 
	var msg = document.getElementById('passwordmsg');
	msg.innerHTML = "Enter a password of at least 8 characters";
	msg.style.visibility='visible';
}

function blurPassword() { 
	document.getElementById('passwordmsg').style.visibility='hidden';
	var cf = document.getElementById('cfpassword_msg');
	cf.style.visibility='hidden';
	if(document.getElementById("password").value.length !== 0 &&
	   document.getElementById("cfpassword").value.length !== 0){
		checkPasswordsMatch();
	}
}

var usernameValid = false;

function validate() {
	checkUsernameFormat();
	checkReCAPTCHA();
	checkPasswordsMatch();
	checkPasswordLength();
	usernameAvailable();
}

function checkUsername() {
	document.getElementById('username_msg').style.visibility='hidden'
	
	//dont check if theres no reason too	
	var uFld = document.getElementById("username").value.trim();
	uFld = uFld.replace(/\s+/, "");
	
	if(!uFld.includes("@") || !uFld.includes(".")) {
		return;
	}
	
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			if(this.responseText === 'true') {
				document.getElementById('username_msg').style.visibility='visible';
				usernameValid = false;
			}
			else if(this.responseText === 'false'){
				usernameValid = true;
			}
		}
	};
	xhttp.open("GET", "checkUsername/" + encodeURIComponent(uFld), true);
	xhttp.send();
}

function usernameAvailable() {
	if(!usernameValid){
		var msg = document.getElementById('username_msg');
		msg.style.visibility='visible';
		msg.innerHTML = 'Username already exists!';
		event.preventDefault();
		return;
	}
}

function checkPasswordsMatch() {
	var pwd = document.getElementById('password').value;
	var cfpwd = document.getElementById('cfpassword').value;
	if(pwd !== cfpwd) {
		document.getElementById('cfpassword_msg').style.visibility='visible';
		event.preventDefault();
		return;
	}
}

function checkPasswordLength() {
	var pwd = document.getElementById("password").value;
	if (pwd.length < 8) {
		document.getElementById('passwordmsg').style.visibility='visible';
		event.preventDefault();
		return;
	}
}

function checkReCAPTCHA(){
	var captcha = document.getElementById('captchamsg');
	captcha.style.visibility='hidden';
	
	if(grecaptcha.getResponse().length === 0) {
		captcha.style.visibility='visible';
		event.preventDefault();
	}
}

function checkUsernameFormat(){
	var username = document.getElementById("username").value.trim();
	username = username.replace(/\s+/, "");

	if(!username.includes("@") || !username.includes(".")) {
		var msg = document.getElementById('username_msg');
		msg.style.visibility='visible';
		msg.innerHTML = 'Invalid Email format';
		event.preventDefault();
		return;
	}
}