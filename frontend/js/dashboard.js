import { firebase, auth, provider, db } from "./firebase.js"


auth.onAuthStateChanged(function (user) {
  if (!user) {
    // User is signed in, redirect to a specific page
    window.location.href = "index.html";
  }
});
const chart = window.Chart

let start = "08-25-2023"
const count_url = `http://127.0.0.1:8000/profitable-count/${start}`;
const profit_url = `http://127.0.0.1:8000/profitabilities/${start}`;
const profit_vs_certainty_url = `http://127.0.0.1:8000/profit-vs-certainty/${start}`

console.log(auth)

fetch(count_url)
  .then(function (response) {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(function (data) {
    createCountChart(data)
  })
  .catch(function (error) {
    document.getElementById('pie-chart-container').style.visibility = "hidden";
    console.error('There was a problem with the fetch operation for the pie chart:', error);
  });

fetch(profit_url)
  .then(function (response) {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(function (data) {
    createProfitableBarChart(data)
  })
  .catch(function (error) {
    document.getElementById('bar-chart-container').style.visibility = "hidden";
    console.error('There was a problem with the fetch operation for the bar chart:', error);
  });

fetch(profit_vs_certainty_url)
  .then(function (response) {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(function (data) {
    createScatterPlot(data)
  })
  .catch(function (error) {
    document.getElementById('scatter-plot-container').style.visibility = "hidden";
    console.error('There was a problem with the fetch operation for scatterplot data:', error);
  });

const createCountChart = (data) => {
  const ctx = document.getElementById('profitable-count-chart');
  const labels = ['Profitable', 'Unprofitable']
  const profitArr = [data["profitable_trades"], data["unprofitable_trades"]]
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        label: '# of Trades',
        data: profitArr,
      }]
    }
  });
}

const createProfitableBarChart = (data) => {
  const tradeHash = new Map();
  data.map((item) => {
    item["trade_time"] = item["trade_time"].split('T')[0]
    if (tradeHash.has(item['trade_time'])) {
      tradeHash.set(item['trade_time'], tradeHash.get(item["trade_time"]) + item['profit'])
    } else {
      tradeHash.set(item['trade_time'], item['profit'])
    }
  })

  const labels = []
  const values = []

  for (const key of tradeHash.keys()) {
    labels.push(key)
  }
  for (const val of tradeHash.values()) {
    values.push(val)
  }

  const ctx = document.getElementById('profitable-bar-chart');
  const dataBar = {
    labels: labels,
    datasets: [{
      label: 'Profitability last 7 days',
      data: values,
      backgroundColor: [
        'rgba(255, 99, 132, 0.2)',
        'rgba(255, 159, 64, 0.2)',
        'rgba(255, 205, 86, 0.2)',
        'rgba(75, 192, 192, 0.2)',
        'rgba(54, 162, 235, 0.2)',
        'rgba(153, 102, 255, 0.2)',
        'rgba(201, 203, 207, 0.2)'
      ],
      borderColor: [
        'rgb(255, 99, 132)',
        'rgb(255, 159, 64)',
        'rgb(255, 205, 86)',
        'rgb(75, 192, 192)',
        'rgb(54, 162, 235)',
        'rgb(153, 102, 255)',
        'rgb(201, 203, 207)'
      ],
      borderWidth: 1
    }]
  };

  const config = {
    type: 'bar',
    data: dataBar,
    options: {
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Dollar Amount'
          }
        },
        x: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Date'
          }
        }
      }
    },
  };

  new Chart(ctx, config)
}

const createScatterPlot = (data) => {
  const ctx = document.getElementById('scatter-plot');
  const scatterData = [];
  data.map((item) => {
    scatterData.push({ x: item["certainty"], y: item["profit_percent"] * 100 })
  })

  // Calculate linear regression
  const sumX = scatterData.reduce((sum, point) => sum + point.x, 0);
  const sumY = scatterData.reduce((sum, point) => sum + point.y, 0);
  const sumXY = scatterData.reduce((sum, point) => sum + point.x * point.y, 0);
  const sumX2 = scatterData.reduce((sum, point) => sum + point.x ** 2, 0);
  const n = scatterData.length;

  const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX ** 2);
  const intercept = (sumY - slope * sumX) / n;

  const yMean = sumY / n;
  const regressionSumSquares = scatterData.reduce((sum, point) => sum + (slope * point.x + intercept - yMean) ** 2, 0);
  const totalSumSquares = scatterData.reduce((sum, point) => sum + (point.y - yMean) ** 2, 0);

  const rSquared = regressionSumSquares / totalSumSquares
  document.getElementById("r-squared").innerText = `R² value: ${rSquared}`

  const scatterPlot = new Chart(ctx, {
    type: "scatter",
    data: {
      datasets: [
        {
          label: "Scatter Data",
          data: scatterData,
          backgroundColor: "blue",
          borderColor: "blue"
        },
        {
          label: "Linear Fit Line",
          type: "line",
          data: scatterData.map(point => ({ x: point.x, y: slope * point.x + intercept })),
          fill: false,
          borderColor: "red"
        }
      ]
    },
    options: {
      scales: {
        x: {
          title: {
            display: true,
            text: 'Model Certainty of Increase'
          }
        },
        y: {
          title: {
            display: true,
            text: "trade profit percentage"
          }
        }
      }
    }
  });
}

const startbot = () => {
  const url = "http://127.0.0.1:8000/startBot/"
    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
    })
      .then(response => response.json())
      .then(data => {
        console.log("Response:", data);
        getBotStatus()
      })
      .catch(error => {
        console.error("Error:", error);
      });
}


const killbot = () => {
  const url = "http://127.0.0.1:8000/killBot/"
    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
    })
      .then(response => response.json())
      .then(data => {
        console.log("Response:", data);
        getBotStatus()
      })
      .catch(error => {
        console.error("Error:", error);
      });
}

document.getElementById("start-button").addEventListener("click", startbot)
document.getElementById("kill-button").addEventListener("click", killbot)

const getBotStatus = () => {
  const url = "http://127.0.0.1:8000/bot-running"
  fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json"
    },
  })
    .then(response => response.json())
    .then(data => {
      console.log("Response:", data);
      const status = document.getElementById("status")
      status.innerText = data ? "Bot Status: Running" : "Bot Status: Off"
    })
    .catch(error => {
      console.error("Error:", error);
    });
}

getBotStatus()
