jQuery(document).ready(function($){
    var canvas = document.getElementById("signature");
    var signaturePad = new SignaturePad(canvas);
    
    $('#clear-signature').on('click', function(){
        signaturePad.clear();
		$(".submit-signature").prop('disabled', true);
    });
    
	$('.submit-signature').on('click', function(){
		if(!signaturePad.isEmpty()){
			var signatureData = signaturePad.toDataURL();
			
			$.post("updatesignature.html",
			{
				userid: $(".submit-signature").attr('id'),
				signature: signatureData
			},
			function(data, status){
				var bdy = $(".bckgrdbdy");
				bdy.empty();
				var e = $('<div class="wrap" id="msg"><h1>Signature Updated!</h1><br><a href="landing.html" style="float:right" class="button2">Home</a></div>');
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
				$(".submit-signature").prop('disabled', false);
			});
		}
    });
	
	signaturePad.onBegin = function() {
		$(".submit-signature").prop('disabled', false)
	};
});