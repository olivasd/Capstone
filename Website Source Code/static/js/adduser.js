var usernameValid = false;

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
				document.getElementById("btnSubmit").disabled = false;
				usernameValid = true;
			}
		}
	};
	xhttp.open("GET", "checkUsername/" + encodeURIComponent(uFld), true);
	xhttp.send();
}

$(document).ready(function() {
	function usernameAvailable() {
		if(!usernameValid){
			var msg = document.getElementById('username_msg');
			msg.style.visibility='visible';
			msg.innerHTML = 'Username already exists!';
			return false;
		}
		return true;
	}

	function checkUsernameFormat(){
		var username = document.getElementById("username").value.trim();
		username = username.replace(/\s+/, "");

		if(!username.includes("@") || !username.includes(".")) {
			var msg = document.getElementById('username_msg');
			msg.style.visibility='visible';
			msg.innerHTML = 'Invalid Email format';
			return false;
		}
		return true;
	}
	
	$("#btnSubmit").click(function(){	
		var f_name = $("#firstname").val().trim();
		var l_name = $("#lastname").val().trim();
		var usr_type = $('input[name=access_level]:checked').val();
		
		if(checkUsernameFormat() &&	usernameAvailable() && f_name != '' && l_name != '')
		{
			$("#btnSubmit").prop('disabled', true);
			$.post("adduser.html",
			{
				username: $("#username").val().trim(),
				fname: f_name,
				lname: l_name,
				type: usr_type
			},
			function(data, status){
				var bdy = $("#bdy");
				bdy.empty();
				var type = ""
				if (usr_type == "0"){ type = "User" }
				else { type = "Admin" }
				var e = $('<div class="wrap" id="msg"><h1>' + type + ' Created!</h1><br><a id="hrf" href="adduser.html" style="float:left" class="button2">Create Another User</a><a href="adminlanding.html" style="float:right" class="button2">Home</a></div>');
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
			.error(function() {
				$("#btnSubmit").prop('disabled', false);
				var msg = document.getElementById('username_msg');
				msg.style.visibility='visible';
				msg.innerHTML = 'Error when creating user!';
			});
		}
    }); 
});