jQuery(document).ready(function($){
    var canvas = document.getElementById("signature");
    var signaturePad = new SignaturePad(canvas);
    
    $('#clear-signature').on('click', function(){
        signaturePad.clear();
		document.getElementById("submit-signature").disabled = true;
    });
    
	$('#submit-signature').on('click', function(){
		submitSignature();
    });
	
	signaturePad.onBegin = function() {
		document.getElementById("submit-signature").disabled = false;
	};

	function submitSignature(){
		if(!signaturePad.isEmpty()){
			var userID = searchCookie("UserId");
			var signatureData = signaturePad.toDataURL();
			
			$.post("submitsignature.html",
			{
				userid: userID,
				signature: signatureData
			},
			function(data, status){
				window.location.href = "/landing.html";
			});
		}	
	}
	
	function searchCookie(cname) {
		var name = cname + "=";
		var ca = document.cookie.split(';');
		for(var i = 0; i < ca.length; i++) {
			var c = ca[i];
			while (c.charAt(0) == ' ') {
				c = c.substring(1);
			}
			if (c.indexOf(name) == 0) {
				return c.substring(name.length, c.length);
			}
		}
		return "";
	}
});