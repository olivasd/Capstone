jQuery(document).ready(function($){
	$("#btnSubmit").click(function(){
		var q1 = $("#question1").val();
		var q2 = $("#question2").val();
		var a1 = $("#answer1").val();
		var a2 = $("#answer2").val();
	
		if(q1 != '' && q2 != '' && a1 != '' & a2 != ''){
			$.post("submitsecurity.html",
			{
				q1id: q1,
				q1ans: a1,
				q2id: q2,
				q2ans: a2,
			},
			function(data, status){
				window.location.href = "capturesignature.html";
			});
		}	
	});
});