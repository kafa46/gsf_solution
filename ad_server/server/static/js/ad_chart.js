// 참고자료: https://seill.tistory.com/1307

var THRESHOLD;
var socket = io();
let socket_id = undefined;
socket.connect(`http://127.0.0.1:8877`);
socket.on('connect', function () {
    socket_id = socket.id;
});

socket.on('anomaly_status', function(anomaly_info){
    // console.log(anomaly_info)
    let status = $('#monitor-status').val();
    if (status === 'start'){
        updateData(anomaly_chart, anomaly_info.z_score);
    } else if (status === 'pause'){
        return;
    } else if (status === 'stop') {
        location.reload()
    }

})

const range = (start, stop, step) =>
    Array.from({ length: (stop - start) / step + 1 }, (_, i) => start + i * step);


var threshold = new Array(100);
// threshold.fill(THRESHOLD);
var anomaly_score = new Array(100);
anomaly_score.fill(0)
var labels = range(1, 100, 1);
var label_idx = 100;

// https://stackoverflow.com/questions/41280857/chart-js-failed-to-create-chart-cant-acquire-context-from-the-given-item
var ctx = $('#anomaly-chart');
var anomaly_chart = new Chart(ctx, {
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
            x: {
                display: true,
                autoSkip: false,
                ticks: {
                    beginAtZero: true,
                    max: THRESHOLD + THRESHOLD,
                }
            },
            y: {
                display: true,
                ticks: {
                    beginAtZero: true,
                    max: THRESHOLD * 2,
                }
            }
        },
    }
});

$(function(){
    // 탐지 모니터링 시작/일시중지/정지 처리
    $('#start').on('click', ()=>{
        $('#monitor-status').val('start')
    });
    $('#pause').on('click', ()=>{
        $('#monitor-status').val('pause')
    });
    $('#stop').on('click', ()=>{
        $('#monitor-status').val('stop')
    });
    
    // 탐지 민감도 변경 처리
    $('#apply-sensitivity').on('click', ()=>{
        form_data = $('#form').serialize()
        $.ajax({
            method: 'POST',
            url: '/threshold/',
            data: form_data,
            data_type: 'json',
            success: function(data){
                console.log(data)
                alert(`민감도 값을 ${data.sensitivity}(threshold: ${data.threshold})으로 설정하였습니다.\n`)
                THRESHOLD = data.threshold
                console.log(THRESHOLD)
                $('.monitor-area').attr('hidden', false);
                threshold.fill(THRESHOLD);
                console.log(threshold)
                anomaly_chart.data.datasets[1].data = threshold
                anomaly_chart.data.datasets[1].label = `Threshold (${THRESHOLD})`
            },
            error: function(request, status, error){
                console.log(error)
            }
        });
    });
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
// setInterval(function () {
//     const newData = gaussianRandom(6, 3, false)
//     updateData(anomaly_chart, newData);
// }, 200);

// function gaussianRandom(mean = 0, stdev = 1, allow_negative = true) {
//     // 가우시안 난수 생성
//     const u = 1 - Math.random(); // Converting [0,1) to (0,1]
//     const v = Math.random();
//     const z = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
//     // Transform to the desired mean and standard deviation:
//     let value = z * stdev + mean;
//     if (allow_negative === false & value < 0.0) {
//         return 0;
//     }
//     return value;
// }