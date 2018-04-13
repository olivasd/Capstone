$(document).ready(function() {
   $('.deleter').click(function() {
	   var ID = this.id;
		$.ajax({
				url: '/deleteaward/' + ID,
				type: 'DELETE',
				success: function(result) {
					$('.' + ID).remove();
				}
		});
	});
});