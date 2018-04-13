
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

function checkPasswordsMatch() {
	var pwd = document.getElementById('password').value;
	var cfpwd = document.getElementById('cfpassword').value;
	if(pwd !== cfpwd) {
		document.getElementById('cfpassword_msg').style.visibility='visible';
		return false;
	}
	return true;
}

function checkPasswordLength() {
	var pwd = document.getElementById("password").value;
	if (pwd.length < 8) {
		document.getElementById('passwordmsg').style.visibility='visible';
		return false;
	}
	return true;
}

$(document).ready(function() {
	$(".btnResetPwd").click(function(){
		if(checkPasswordLength() && checkPasswordsMatch()){
			$(".btnResetPwd").prop('disabled', true);
			
			$.post("userchangepwd",
			{
				id: $(".btnResetPwd").attr('id'),
				pwd: $("#password").val()
			},
			function(data, status){
				var bdy = $(".bckgrdbdy");
				bdy.empty();
				var e = $('<div class="wrap" id="msg"><h1>Password Updated!</h1><br><a href="landing.html" style="float:right" class="button2">Home</a></div>');
				bdy.append(e);
				var messg = $('#msg');
				messg.css({	
					"position" : "absolute",
					"width" : "600px",
					"height" : "300px",
					"top" : "0",
					"left" : "0",
					"bottom" : "0",
					"right" : "0",	
					"margin" : "auto"
				});	
			})
			.error(function() {
				$(".btnResetPwd").prop('disabled', false);
			});	
		}	
	});
	
    $("#btnSubmit").click(function(){	
		var f_name = $("#firstname").val();
		var l_name = $("#lastname").val();
		
		if(f_name != '' || l_name != '')
		{
			$("#btnSubmit").prop('disabled', true);

			$.post("edituserprofile.html",
			{
				fname: f_name,
				lname: l_name
			},
			function(data, status){
				var bdy = $(".bckgrdbdy");
				bdy.empty();
				var e = $('<div class="wrap" id="msg"><h1>Profile Updated!</h1><br><a href="landing.html" style="float:right" class="button2">Home</a></div>');
				bdy.append(e);
				var messg = $('#msg');
				messg.css({	
					"position" : "absolute",
					"width" : "600px",
					"height" : "300px",
					"top" : "0",
					"left" : "0",
					"bottom" : "0",
					"right" : "0",	
					"margin" : "auto"
				});	
			})
			.error(function() {
				$("#btnSubmit").prop('disabled', false);
			});
		}
    }); 
});