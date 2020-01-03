function graph(graphtitle, input) {
    // This is a function used to create the graph in JQPlot
    plot1 = $.jqplot('chart1', input, {
        //note: jqplot wants the input coordinates to be a doubly nested array.
        title: graphtitle,
        animate: true,
        series: [{
            markerOptions: {
                size: 10,
                style: "filledCircle"
            },
            pointLabels: {
                show: true
            },
            rendererOptions: {
                animation: {
                    speed: 2000
                }
            },
            showLine: false
        }],
        seriesDefaults: {
            breakOnNull: true,
        },
        axesDefaults: {
            tickRenderer: $.jqplot.CanvasAxisTickRenderer,
            labelRenderer: $.jqplot.CanvasAxisLabelRenderer,
            tickOptions: {
                angle: -20,
            },
        },
        axes: {
            // options for each axis are specified in seperate option objects.
            xaxis: {
                show: false,
                label: "Day in the week",
                pad: 2,
                min: 0,
                max: input[0].length + 1,
                tickInterval: 1
            },
            yaxis: {
                label: "Answer",
                labelOptions: {
                    angle: 0
                },
                min: 0,
                max: input[0].max() + 1,
                tickInterval: 1,
                pad: 2
            },
        },
        seriesColors: ["#7BB661", "#E03C31"],
        highlighter: {
            show: true,
            showLabel: true,
            yvalues: 3,
            tooltipAxes: 'y',
            formatString: "%d",
            sizeAdjust: 7.5,
            tooltipLocation: 'ne'
        }
    });
}


function replot_user_results(title, data) {
    //clears the graph, plots to supplied coordinates
    console.log("title:");
    console.log(title);
    console.log("data:");
    console.log(data);
    console.log(data[0].max());
    $('#chart1').empty();
    graph(title, data);
}


// Used in this JS to make the graph look better..
Array.prototype.max = function() {
    var max = this[0];
    var len = this.length;
    for (var i = 1; i < len; i++)
        if (this[i] > max) max = this[i];
    return parseInt(max);
}