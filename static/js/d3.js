
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

  // Define data for amortization schedule
  var schedule_url = "/schedule_d3";

  // Import data from amortization schedule data
  d3.json(schedule_url).then(function(scheduleData){

    // console.log(scheduleData);

    // Create function to parse date and time
    var parseTime = d3.timeParse("%Y-%m-%d");

    // Format the data
    scheduleData.forEach(function(data) {
      data.payment_date = parseTime(data.payment_date);
      data.ending_balance = +data.ending_balance;
      data.cumulative_interest = +(data.cumulative_interest * -1);
      console.log(data);
    });


    // Create the scales for the chart
    // x-axis
    var xTimeScale = d3.scaleTime()
      .domain(d3.extent(scheduleData, data => data.payment_date))
      .range([0, chartWidth]);
    // y-axis
    var yLinearScale = d3.scaleLinear()
      .range([chartHeight, 0]);

    // Set up the y-axis domain
    // find the max ending balance
    var ending_balance_max = d3.max(scheduleData, d => d.ending_balance);
    // find the max cumulative interest data
    var cumulative_interest_max = d3.max(scheduleData, d => d.cumulative_interest);

    var yMax;
    if (ending_balance_max > cumulative_interest_max) {
      yMax = ending_balance_max;
    }
    else {
      yMax = cumulative_interest_max;
    }

    // Use the yMax value to set the yLinearScale domain
    yLinearScale.domain([0, yMax]);

    // Create the axes
    var bottomAxis = d3.axisBottom(xTimeScale).tickFormat(d3.timeFormat("%Y-%m-%d"));
    var leftAxis = d3.axisLeft(yLinearScale);


    chartGroup.append("g")
      .attr("transform", `translate(0, ${chartHeight})`)
      .call(bottomAxis);

    // Add y-axis
    chartGroup.append("g").call(leftAxis);


    // Line generator for ending balance data
    var line1 = d3.line()
      .x(d => xTimeScale(d.payment_date))
      .y(d => yLinearScale(d.ending_balance));

    // Line generator for cumulative interest data
    var line2 = d3.line()
      .x(d => xTimeScale(d.payment_date))
      .y(d => yLinearScale(d.cumulative_interest));


    // Append a path for line1
    chartGroup
      .append("path")
      .attr("d", line1(scheduleData))
      .classed("line green", true);

    // Append a path for line2
    chartGroup
      .data([scheduleData])
      .append("path")
      .attr("d", line2)
      .classed("line orange", true);

    // Create Legends


  }).catch(function(error) {
      console.log(error);
  });

}

amortizationSchedule();
