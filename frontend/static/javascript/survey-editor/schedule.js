var days_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];


// Return the time as an h:MM AM/PM string instead of as a number of seconds past midnight
Handlebars.registerHelper("int_to_time", function(number_of_seconds) {
    var time_string = "";

    // Add hours (in 12-hour time)
    var hours = Math.floor(number_of_seconds / 3600) % 12;
    if (hours == 0) {
        hours = 12;
    }
    time_string += hours + ":";

    // Add minutes
    var minutes = Math.floor((number_of_seconds % 3600) / 60);
    if (minutes < 10) {
        time_string += "0" + minutes;
    } else {
        time_string += minutes;
    };

    // Add AM/PM
    if (number_of_seconds < 3600 * 12) {
        time_string += " AM";
    } else {
        time_string += " PM";
    };

    return time_string;
});


function renderSchedule() {
    var source = $("#schedule-template").html();
    var template = Handlebars.compile(source);

    var schedule = [];
    for (var i=0; i<7; i++) {
    	day_schedule = {day_name: days_list[i], times: survey_times[i]};
    	schedule.push(day_schedule);
    };

    var dataList = {schedules: schedule};
    var htmlSchedule = template(dataList);

    $('#surveySchedule').html(htmlSchedule);
}


function add_time() {
    var time_string = $('#new_time_timepicker').val();
    var hours = parseInt(time_string.split(':')[0]);
    if (hours == 12) {
        hours = 0;
    }
    var minutes = parseInt(time_string.split(':')[1]);
    var am_pm = time_string.split(' ')[1];
    var number_of_seconds = (hours * 3600) + (minutes * 60);
    if (am_pm == 'PM') {
        number_of_seconds += (12 * 3600);
    };

    var day_index = $('#day_index_select').val();

    if (day_index == "every_day") {
        // If they selected "every_day", add this time to all 7 days
        for (var i = 0; i < 7; i++) {
            add_time_to_day_index(number_of_seconds, i);
        };
    } else {
        // Otherwise, just add this time to the selected day
        add_time_to_day_index(number_of_seconds, day_index);
    };

    // Re-render the schedule
    renderSchedule();
}


function add_time_to_day_index(time, day_index) {
    survey_times[day_index].push(time);
    survey_times[day_index].sort();
}


function delete_time(day_index, time_index) {
    survey_times[day_index].splice(time_index, 1);
    renderSchedule();
}
