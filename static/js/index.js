jQuery(document).ready(function(){

	$('input:radio[name="gender_confirm"]').change(function(){
    	//console.log("CHANGED HERE..");
    	$("form").attr("action", "/log_result");
	});

});
