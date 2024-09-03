

const range = (start, stop, step) =>
    Array.from({ length: (stop - start) / step + 1 }, (_, i) => start + i * step);

const THRESHOLD = 12;

var threshold = new Array(100);
threshold.fill(THRESHOLD);
var anomaly_score = new Array(100);
anomaly_score.fill(0)
var labels = range(1, 100, 1);
var label_idx = 100;

var anomaly_chart = new Chart("Chart", {
    type: "line",
    data: {
        labels: labels,
        datasets: [{
            label: 'Anomaly Score',
            data: anomaly_score,
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1,
            fill: false,
            lineTension: 0.1
        },
        {
            label: `Threshold (${THRESHOLD})`,
            data: threshold,
            borderColor: "green",
            fill: false
        }]
    },
    options: {
        legend: { display: false },
        scales: {
            xAxes: [{
                display: true,
                autoSkip: false,
                ticks: {
                    beginAtZero: true,
                    max: THRESHOLD + THRESHOLD*0.5,
                }
            }],
            yAxes: [{
                display: true,
                ticks: {
                    beginAtZero: true,
                    max: THRESHOLD * 2,
                }
            }]
        },
    }
});

function updateData(chart, data) {
    label_idx++;
    labels.shift();
    labels.push(label_idx)
    anomaly_score.shift();
    anomaly_score.push(data);
    chart.update();
}

// 데이터를 업데이트하는 함수를 1000ms(1초)마다 실행
setInterval(function () {
    const newData = gaussianRandom(6, 3, false)
    updateData(anomaly_chart, newData);
}, 200);


// 참고자료: https://seill.tistory.com/1307
// const THRESHOLD = 10;
// var dataIndex = 0;
// var ctx = document.getElementById('Chart').getContext('2d');
// var anomaly_chart = new Chart(ctx, {
//     type: 'line',
//     data: {
//         labels: [], // 초기 라벨(시간)은 비워둠
//         datasets: [
//             {
//               label: 'Dataset 1',
//               data: [1, 3, 5, 8, 4],
//               borderColor: 'red',
//             //   backgroundColor: Utils.transparentize(Utils.CHART_COLORS.red, 0.5),
//             },
//             {
//               label: 'Dataset 2',
//               data: [7, 7, 7, 7, 7],
//               borderColor: 'blue',
//             //   backgroundColor: Utils.transparentize(Utils.CHART_COLORS.blue, 0.5),
//             }
//           ]
//     },
//     options: {
//         responsive: true,
//         plugins: {
//           legend: {
//             position: 'top',
//           },
//           title: {
//             display: true,
//             text: 'Chart.js Line Chart'
//           }
//         }
//       },    
//     // options: {
//     //     animation: false, // 실시간 성능을 위해 애니메이션 비활성화
//     //     scales: {
//             // xAxes: [{
//             //     type: 'linear',
//             //     position: 'bottom',
//             //     ticks: []
//             // }]
//             // x: {
//             //     type: 'linear',
//             //     position: 'bottom'
//             // },
//             // y: {
//             //     type: 'linear',
//             //     display: true,
//             //     position: 'left',
//             // },
//             // y1: {
//             //     type: 'linear',
//             //     display: true,
//             //     position: 'right',
//             //     // grid line settings
//             //     grid: {
//             //         drawOnChartArea: false, // only want the grid lines for one axis to show up
//             //     },
//             // },
//         }
//     }
// });

// function addData(chart, label, data) {
//     chart.data.labels.push(label);
//     if (chart.data.labels.length > 100) { // 최대 데이터 포인트 수를 100으로 제한
//         chart.data.labels.shift(); // 가장 오래된 라벨 제거
//         chart.data.datasets.forEach((dataset) => {
//             dataset.data.shift(); // 가장 오래된 데이터 포인트 제거
//         });
//     }

//     let anomaly = {x: label, y: data, y1: THRESHOLD}

//     for (let i = 0; i < chart.data.datasets.length; i++) {
//         chart.data.datasets[0].data.push(anomaly)
//         // chart.data.datasets[1].data.push(threshold)
//         // chart.options.scales.xAxes.ticks = chart.data.labels
//     }
//     // for (let i = 0; i < chart.data.datasets.length; i++) {
//     //     chart.data.datasets[0].data.push(data)
//     //     chart.data.datasets[1].data.push(THRESHOLD)
//     // }
//     // chart.data.datasets.forEach((dataset) => {
//     //     dataset.data[0].push(data);
//     //     dataset.data[1].push(THRESHOLD);
//     // });
//     chart.update();
// }



// 데이터를 업데이트하는 함수를 1000ms(1초)마다 실행
// setInterval(function () {
//     const newData = gaussianRandom(6, 3, false)
//     addData(anomaly_chart, dataIndex, newData);
//     dataIndex++;
// }, 200);


function gaussianRandom(mean = 0, stdev = 1, allow_negative = true) {
    // 가우시안 난수 생성
    const u = 1 - Math.random(); // Converting [0,1) to (0,1]
    const v = Math.random();
    const z = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
    // Transform to the desired mean and standard deviation:
    let value = z * stdev + mean;
    if (allow_negative === false & value < 0.0) {
        return 0;
    }
    return value;

}