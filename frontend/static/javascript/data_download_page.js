$(document).ready(function() {
	/* Set up Date/Time pickers */
    $('#start_datetimepicker').datetimepicker();
    $('#end_datetimepicker').datetimepicker();

	/* When the form gets submitted, reformat the DateTimes into ISO UTC format */
	$('#data_download_parameters_form').submit(submit_clicked);
});


function submit_clicked() {
		$("#explanation_paragraph").show()
		format_datetimepickers();
		$('#download_submit_button').prop('disabled', true);
		return true;
};


function format_datetimepickers() {
	/* If they're empty, remove this value from the POST request */
	if ($('#start_datetime').val()) {
		$('#start_datetime').val(moment($('#start_datetime').val()).format('YYYY-MM-DDTHH:mm:ss'));
	} else {
		$('#start_datetime').attr('disabled', 'disabled');
	};
	if ($('#end_datetime').val()) {
		$('#end_datetime').val(moment($('#end_datetime').val()).format('YYYY-MM-DDTHH:mm:ss'));
	} else {
		$('#end_datetime').attr('disabled', 'disabled');
	};
};