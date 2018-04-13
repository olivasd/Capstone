var usernameValid = true;

function checkUsername() {
	document.getElementById('username_msg').style.visibility='hidden'
	
	//dont check if theres no reason too	
	var uFld = document.getElementById("username").value.trim();
	uFld = uFld.replace(/\s+/, "");
	
	var u_placeholder = document.getElementById("username").getAttribute("placeholder");
	
	if(uFld == '') { return; }
	else if(!uFld.includes("@") || !uFld.includes(".")){
		usernameValid = false;
		return;
	}
	
	if(u_placeholder == uFld) { 
		usernameValid = true;
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
				(document.getElementsByClassName("btnsub")[0]).disabled = false;
				usernameValid = true;
			}
		}
	};
	xhttp.open("GET", "checkUsername/" + encodeURIComponent(uFld), true);
	xhttp.send();
}

$(document).ready(function() {
	$("#btnSubmit").prop('disabled', true);
	
	$("#firstname").blur(function() {
		if($("#firstname").val() != '') {
			$("#btnSubmit").prop('disabled', false);
		}
	});
	
	$("#lastname").blur(function() {
		if($("#lastname").val() != '') {
			$("#btnSubmit").prop('disabled', false);
		}
	});
	
	$(".resetpwd").click(function(){
		$(".resetpwd").prop('disabled', true);

		$.post("forceresetpassword",
		{
			id: $(".resetpwd").attr('id')
		},
		function(data, status){
			var bdy = $(".bckgrdbdy");
			bdy.empty();
			var e = $('<div class="wrap" id="msg"><h1>Reset Password Sent!</h1><br>');
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
			$(".resetpwd").prop('disabled', false);
		});
	});
	
    $(".btnsub").click(function(){	
		var f_name = $("#firstname").val();
		var l_name = $("#lastname").val();
		var u_name = $("#username").val();
		
		if($("#username").val() == '') { usernameValid = true; }
		
		if((f_name != '' || l_name != '' || u_name != '') && usernameValid)
		{
			$("#btnSubmit").prop('disabled', true);

			$.post("editusers.html",
			{
				fname: ($("#firstname").val() == '' ? $("#firstname").attr('placeholder') : $("#firstname").val()),
				lname: ($("#lastname").val() == '' ? $("#lastname").attr('placeholder') : $("#lastname").val()),
				username: ($("#username").val() == '' ? $("#username").attr('placeholder') : $("#username").val()),
				id: $(".btnsub").attr('id')
			},
			function(data, status){
				var bdy = $(".bckgrdbdy");
				bdy.empty();
				var e = $('<div class="wrap" id="msg"><h1>Profile Updated!</h1><br><a href="adminlanding.html" style="float:right" class="button2">Home</a></div>');
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