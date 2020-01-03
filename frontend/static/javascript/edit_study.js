$(document).ready(function(){
	enable_import_file_button_if_file_selected();

	$('#file_upload_selector').change(function(){
		enable_import_file_button_if_file_selected();
	});
});

/* The "Import Study Settings File" button is disabled until the user chooses a file to upload */
function enable_import_file_button_if_file_selected() {
	if ($('#file_upload_selector').val() != "") {
		$('#file_upload_button').prop('disabled', false);
	};
};
