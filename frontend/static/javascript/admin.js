$(document).ready(function(){

    // Set up the main list of patients using DataTables
    $("#pipelines_list").DataTable({
        dom: 'Bfrtip',
        "order": [[1, "desc" ]],
        buttons: [
            'csv', 'excel', 'pageLength'
        ],
        "pageLength": 5,
        "lengthMenu": [[5, 10, 25, 50, 100, 500, 1000, -1], [5, 10, 25, 50, 100, 500, 1000, "All"]],
    });

    // Set up the main list of patients using DataTables
    $("#total_upload_stats").DataTable({
        dom: 'Bfrtip',
        buttons: [
            'csv', 'excel', 'pageLength'
        ],
        "pageLength": 5,
        "lengthMenu": [[5, 10, 25, 50, 100, 500, 1000, -1], [5, 10, 25, 50, 100, 500, 1000, "All"]],
    });

    // Set up the main list of files to process using DataTables
    $("#files_to_process_table").DataTable({
        dom: 'Bfrtip',
        "order": [[0, "asc"]],
        buttons: [
            'csv', 'excel', 'pageLength'
        ],
        "pageLength": 25,
        "lengthMenu": [[5, 10, 25, 50, 100, 500, 1000, -1], [5, 10, 25, 50, 100, 500, 1000, "All"]],
    });

    // Set up the main list of patients using DataTables
    $("#patients_list").DataTable({
        dom: 'Bfrtip',
        "order": [[2, "asc"]],
        buttons: [
            'csv', 'excel', 'pageLength'
        ],
        "pageLength": 25,
        "lengthMenu": [[5, 10, 25, 50, 100, 500, 1000, -1], [5, 10, 25, 50, 100, 500, 1000, "All"]],
    });

    // Set up the main list of patients using DataTables
    $("#patients_statistics").DataTable({
        dom: 'Bfrtip',
        "order": [[2, "asc"]],
        buttons: [
            'csv', 'excel', 'pageLength'
        ],
        "pageLength": 25,
        "lengthMenu": [[5, 10, 25, 50, 100, 500, 1000, -1], [5, 10, 25, 50, 100, 500, 1000, "All"]],
    });

    // Set up the main list of patients using DataTables
    $("#alias_list").DataTable({
        dom: 'Bfrtip',
        buttons: [
            'csv', 'excel', 'pageLength'
        ],
        "pageLength": 5,
        "lengthMenu": [[5, 10, 25, 50, 100, 500, 1000, -1], [5, 10, 25, 50, 100, 500, 1000, "All"]],
    });

    $('#many-new-patients-loading-spinner').hide();

    $('#createManyPatientsForm').on('submit', function(e){
        $('#createManyPatientsButton').prop('disabled', true);  // Disable the button so they can't click it twice
        $('#many-new-patients-loading-spinner').show();
        $('#many-new-patients-submit-and-cancel-buttons').hide();
    });

    $('#addManyPatientsModal').on("hidden.bs.modal", function() {
        location.reload();
    });
});

function logout() {
    window.location.href="/logout";
}

/* Pop up a confirmation dialog and only delete the study if the user types an EXACT string */
function confirm_delete_study(study_name, study_id) {
    var required_matching_text = "Yes, I want to delete " + study_name;
    var prompt_message = "Are you ABSOLUTELY SURE that you want to delete the study " + study_name +" and all users and surveys associated with it?\nIf you're DEAD CERTAIN, type '" + required_matching_text + "' in the box here:";
    var confirmation_prompt = prompt(prompt_message);
    if (confirmation_prompt == required_matching_text) {
        $.ajax({
            type: 'POST',
            url: '/delete_study/' + study_id,
            data: {
                confirmation: "true"
            }
        }).done(function() {
            location.href = "/manage_studies";
        }).fail(function() {
            alert("There was a problem with deleting the study.");
        });
    };
}
