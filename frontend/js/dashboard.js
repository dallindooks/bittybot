import { firebase, auth, provider, db } from "./firebase.js"


auth.onAuthStateChanged(function (user) {
    if (!user) {
        // User is signed in, redirect to a specific page
        window.location.href = "index.html";
    }
});
const chart = window.Chart

let start = "08-25-2023"
const url = `http://127.0.0.1:8000/profitable-count/${start}`;

fetch(url)
    .then(function(response) {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(function(data) {
        createChart(data)
    })
    .catch(function(error) {
        console.error('There was a problem with the fetch operation:', error);
    });

const createChart = (data) => {
  const ctx = document.getElementById('myChart');
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