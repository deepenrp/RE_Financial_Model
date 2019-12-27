
var schedule_url = "/schedule_plotly";

function amortizationSchedule() {
  
  d3.json(schedule_url).then(function(data){

    var parseTime = d3.timeParse("%Y");
    var payment_date = data.payment_date;
    var ending_balance = data.ending_balance;
    var cumulative_principal = data.cumulative_principal.map(function(x) { return x * -1; });
    var cumulative_interest = data.cumulative_interest.map(function(x) { return x * -1; });
    // console.log(payment_date);
    // console.log(cumulative_interest);
    // console.log(cumulative_principal);
    // console.log(ending_balance);

    var trace1 = {
        x: payment_date,
        y: ending_balance,
        mode: 'lines',
        name: 'Ending Balance'
      };
      
    var trace2 = {
      x: payment_date,
      y: cumulative_principal,
      mode: 'lines',
      name: 'Cumulative Principal'
      };
    
    var trace3 = {
      x: payment_date,
      y: cumulative_interest,
      mode: 'lines',
      name: 'Cumulative Interest'
      };
    
    var data = [trace1, trace2, trace3];
    
    var layout = {
      title: 'Amortization Schedule',
      xaxis: {
        title: 'Payment Date'
        },
      yaxis: {
        title: 'Amortization ($)'
        }
      // showlegend: true,
      // legend: {
      //   xanchor:"center",
      //   yanchor:"top",
      //   y: 0.50,
      //   x: 0.75
      //   }
      };
      
    Plotly.newPlot("schedule", data, layout);



    }).catch(function(error) {
      console.log(error);

      });
  }


// ------------------------------------------------------------------------------------------


var equity_url = "/equity_plotly";

function equityChart() {

  d3.json(equity_url).then(function(data){

    var payment_date = data.payment_date;
    var equity_from_appreciation = data.equity_from_appreciation;

    var trace1 = {
      x: payment_date,
      y: equity_from_appreciation,
      mode: 'lines',
      name: 'Equity from Appreciation'
    };

    var data = [trace1];

    var layout = {
      title: 'Equity through Appreciation',
      xaxis: {
        title: 'Payment Date'
        },
      yaxis: {
        title: 'Equity through Appreciation ($)'
        }
      // showlegend: true,
      // legend: {
      //   xanchor:"center",
      //   yanchor:"top",
      //   y: 0.50,
      //   x: 0.75
      //   }
      };

      Plotly.newPlot("appreciation", data, layout);


  }).catch(function(error) {
    console.log(error);

    });
}

// ------------------------------------------------------------------------------------------

var ten_year_url = "/ten_years_plotly";

function tenYearChart() {

  d3.json(ten_year_url).then(function(data){

    var months = data.month;
    var wealth_created = data.wealth_created;

    console.log(months);

    var trace1 = {
      x: months,
      y: wealth_created,
      type: 'bar',
      marker: {
        color: 'green'
      }
    };
    
    var data = [trace1];

    var layout = {
      title: 'Wealth Created',
      font:{
        family: 'Calibri, sans-serif'
      },
      showlegend: false,
      xaxis: {
        xlabel: "Month",
        tickangle: 0
      },
      yaxis: {
        zeroline: true,
        gridwidth: 0
      },
      bargap :0.05
    };

    Plotly.newPlot('wealth', data, layout);

}).catch(function(error) {
  console.log(error);

  });
}

amortizationSchedule();
equityChart();
tenYearChart();
   