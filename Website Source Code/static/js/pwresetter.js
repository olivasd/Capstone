var saved_user_id = '';
var saved_q1_id = '';
var saved_q2_id = '';

function checkPasswordsMatch() {
	var pwd = document.getElementById('password').value;
	var cfpwd = document.getElementById('cfpassword').value;
	if(pwd !== cfpwd) {
		document.getElementById('cfpassword_msg').style.visibility='visible';
		return false;
	}
	return true;
};

function checkPasswordLength() {
	var pwd = document.getElementById("password").value;
	if (pwd.length < 8) {
		document.getElementById('passwordmsg').style.visibility='visible';
		return false;
	}
	return true;
};

function blurConfirmPW() {
	document.getElementById('cfpassword_msg').style.visibility='hidden';
	checkPasswordsMatch();
};

function focusPassword() { 
	var msg = document.getElementById('passwordmsg');
	msg.innerHTML = "Enter a password of at least 8 characters";
	msg.style.visibility='visible';
};

function blurPassword() { 
	document.getElementById('passwordmsg').style.visibility='hidden';
	var cf = document.getElementById('cfpassword_msg');
	cf.style.visibility='hidden';
	if(document.getElementById("password").value.length !== 0 &&
	   document.getElementById("cfpassword").value.length !== 0){
		checkPasswordsMatch();
	}
};
	
$(document).ready(function() {
	$("#btnSubmitEmail").click(function(){
		var user_name = $("#username");
					
		if(user_name.val().length !== 0){
			$.post("testusernameforreset",
			{
				username: user_name.val()
			},
			function(data, status){
				var obj = jQuery.parseJSON(data);
				saved_user_id = obj.userid;
				saved_q1_id = obj.question1id;
				saved_q2_id = obj.question2id;
				$('#question1').text(obj.question1);
				$('#question2').text(obj.question2);
				$("#part1").remove();
				$("#part2").css('visibility', 'visible')
			})
			.fail(function(){
				user_name.css('border-color', 'red');
			});
		}
	});
	
	$("#btnSubmitReset").click(function(){
		var ans1 = $("#answer1");
		var ans2 = $("#answer2");
		
		if(ans1.val().length === 0){
			ans1.css('border-color', 'red');
			return;
		}
		
		if(ans2.val().length === 0){
			ans2.css('border-color', 'red');
			return;
		}
		
		if(checkPasswordsMatch() && checkPasswordLength()){
			$.post("tryresetpassword",
			{
				userid: saved_user_id,
				q1id: saved_q1_id,
				q2id: saved_q2_id,
				q1ans: ans1.val(),
				q2ans: ans2.val(),
				pword: $("#password").val()
			},
			function(data, status){
				var bdy = $("#bdy");
				bdy.empty();
				var e = $('<div class="wrap" id="msg"><h1>Password Reset!</h1><br><a id="hrf" href="/" style="float:left" class="button2">Back to Login</a></div>');
				bdy.append(e);
				var messg = $('#msg');
				messg.css({	
					"position" : "absolute",
					"width" : "600px",
					"height" : "300px",
					"top" : "0",
					"bottom" : "0",
					"left" : "0",
					"right" : "0",	
					"margin" : "auto"
				});	
			})
			.fail(function(){
				$("#result_msg").css('visibility', 'visible')
			});;
		}
	});
});