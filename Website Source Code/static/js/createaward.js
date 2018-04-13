$(document).ready(function() {
    $("#btnSubmit").click(function(){	
		var date = $("#datepicker").datepicker("getDate");
		var formatted_date = $.datepicker.formatDate("yy-mm-dd", date);
		var user_value = $("#user").val();
		var time = $("#time_entry").val();

		if(formatted_date != '' && user_value != null && time != '')
		{
			$("#btnSubmit").prop('disabled', true);
			$("#loading-bar-spinner").removeAttr("style");
			$.post("createaward.html",
			{
				type: $('input[name=award]:checked').val(),
				receivngUser: user_value,
				date: formatted_date,
				time: time
			},
			function(data, status){
				var bdy = $("#bdy");
				bdy.empty();
				var e = $('<div class="wrap" id="msg"><h1>Award Sent!</h1><br><a id="hrf" href="createaward.html" style="float:left" class="button2">Create Another Award</a><a href="landing.html" style="float:right" class="button2">Home</a></div>');
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
				$("#loading-bar-spinner").css('display','none');
			});
		}
    }); 
});