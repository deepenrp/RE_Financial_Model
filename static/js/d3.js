
function amortizationSchedule() {


  // Define SVG area dimensions
  var svgWidth = 500;
  var svgHeight = 300;

  // Define the chart's margins as an object
  var margin = {
    top: 5,
    right: 5,
    bottom: 50,
    left: 50
  };

  // Define dimensions of the chart area
  var chartWidth = svgWidth - margin.left - margin.right;
  var chartHeight = svgHeight - margin.top - margin.bottom;

  // Select body, append SVG area to it, and set its dimensions
  var svg = d3.select("#schedule")
    .append("svg")
    .attr("width", svgWidth)
    .attr("height", svgHeight);

  // Append a group area, then set its margins
  var chartGroup = svg.append("g")
    .attr("transform", `translate(${margin.left}, ${margin.top})`);


  var schedule_url = "/schedule_d3";

  

  d3.json(schedule_url).then(function(scheduleData){

    // console.log(scheduleData);
    var parseTime = d3.timeParse("%Y-%m-%d");

    // Format the date and cast the force value to a number
    scheduleData.forEach(function(data) {
      console.log(data);
      data.payment_date = parseTime(data.payment_date);
      data.ending_balance = +data.ending_balance;
      data.cumulative_interest = +data.cumulative_interest;
    });


    // d3.extent returns the an array containing the min and max values for the property specified
    var xTimeScale = d3.scaleTime()
      .domain(d3.extent(scheduleData, data => data.payment_date))
      .range([0, chartWidth]);

    // Configure a linear scale with a range between the chartHeight and 0
    var yLinearScale = d3.scaleLinear()
      .range([chartHeight, 0]);

    var ending_balance_max = d3.max(scheduleData, data => data.ending_balance);

    var cumulative_interest_max = d3.max(scheduleData, data => data.cumulative_interest);

    var yMax;
    if (ending_balance_max > cumulative_interest_max) {
      yMax = ending_balance_max;
    }
    else {
      yMax = cumulative_interest_max;
    }

    yLinearScale.domain([0, yMax]);

    var bottomAxis = d3.axisBottom(xTimeScale).tickFormat(d3.timeFormat("%Y-%m-%d"));
    var leftAxis = d3.axisLeft(yLinearScale);


    chartGroup.append("g")
      .attr("transform", `translate(0, ${chartHeight})`)
      .call(bottomAxis);

    // Add y-axis
    chartGroup.append("g").call(leftAxis);


    // Line generator for ending balance data
    var line1 = d3.line()
      .x(data => xTimeScale(data.payment_date))
      .y(data => yLinearScale(data.ending_balance));

    // Line generator for cumulative interest data
    var line2 = d3.line()
      .x(data => xTimeScale(data.payment_date))
      .y(data => yLinearScale(data.cumulative_interest));


    // Append a path for line1
    chartGroup
      .append("path")
      .attr("data", line1(scheduleData))
      .classed("line green", true);

    // Append a path for line2
    chartGroup
      .data([scheduleData])
      .append("path")
      .attr("data", line2)
      .classed("line orange", true);




  }).catch(function(error) {
      console.log(error);
  });

}

amortizationSchedule();



