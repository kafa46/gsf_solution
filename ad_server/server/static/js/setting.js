document.addEventListener('DOMContentLoaded', function() {
    
    // FastAPI 서버로부터 카메라 목록을 가져오는 함수
    function refreshCameraList() {
        fetch('http://localhost:8899/available_cameras')
            .then(response => response.json())
            .then(data => {
                const cameraSelect = document.getElementById('cameraSelect');
                cameraSelect.innerHTML = '<option value="">Select a camera</option>';
                data.available_cameras.forEach(cameraIndex => {
                    const option = document.createElement('option');
                    option.value = cameraIndex;
                    option.text = `Camera ${cameraIndex}`;
                    cameraSelect.appendChild(option);
                });
            });
    }

    // 카메라 열기 버튼 클릭 시 스트리밍을 시작하는 함수
    function startStreaming() {
        const selectedCamera = document.getElementById('cameraSelect').value;
        if (selectedCamera !== "") {
            const videoFeed = document.getElementById('videoFeed');
            // 선택한 카메라 번호를 쿼리 매개변수로 전송하여 스트리밍 요청
            videoFeed.src = `http://localhost:8899/video_feed?camera_index=${selectedCamera}`;
        } else {
            alert("Please select a camera.");
        }
    }

    // 테이블 열 데이터 가져오기
    function collectTableData(){
        const tableBody = document.getElementById('configTableBody'); // 테이블 본문 요소 가져오기
        const rows = tableBody.querySelectorAll('tr') // 테이블의 모든 행 가져오기
        const setting_list = []; 

        // 각 행에 대해 데이터 저장
        rows.forEach((row, index) =>{
            const margin = row.querySelector('input[name="margin"]').value;
            const lower_bound = row.querySelector('input[name="lower_bound"]').value;
            const upper_bound = row.querySelector('input[name="upper_bound"]').value;
            
            // 저장한 데이터를 array에 추가 
            setting_list.push({
                rowIndex: index + 1, // 행의 순번 (1부터 시작)
                margin: parseFloat(margin),
                lower_bound: parseFloat(lower_bound),
                upper_bound: parseFloat(upper_bound)
            });
        });
        
        return setting_list;
    }

    // 이미지 처리 요청
    function requestProcessing() {
        // 테이블에 입력된 rowIndex, margin, lower_bound, upper_bound를 http://localhost:8899/processed_image
        const tableData = collectTableData()
        
        // FastAPI 서버에 데이터 전송
        fetch('http://localhost:8899/image_processing', {
            method: 'POST',
            headers: {
                'Content-Type' : 'application/json'
            },
            body: JSON.stringify(tableData) // 수집된 테이블 데이터를 JSON 형식으로 전송
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            // 처리된 이미지가 반환되면 화면에 표시하는 로직을 추가
            alert
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error occurred while processing the image.');
        });
    }
    

    // Function to handle row addition
    document.getElementById('addRowBtn').addEventListener('click', function() {
        const tableBody = document.getElementById('configTableBody');
        const rowCount = tableBody.rows.length + 1;
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td>${rowCount}</td>
            <td><input type="number" class="form-control" name="margin" placeholder="Enter Margin"></td>
            <td><input type="number" class="form-control" name="lower_bound" placeholder="Enter Lower Bound"></td>
            <td><input type="number" class="form-control" name="upper_bound" placeholder="Enter Upper Bound"></td>
            <td><button type="button" class="btn btn-outline-danger btn-sm remove-row">삭제</button></td>
        `;
        tableBody.appendChild(newRow);
    });

    // Function to handle row removal
    document.getElementById('configTableBody').addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-row')) {
            e.target.closest('tr').remove();
        }
    });
    
    // 새로고침 버튼 클릭 이벤트
    document.getElementById('refreshBtn').addEventListener('click', refreshCameraList);

    // 카메라 열기 버튼 클릭 시 스트리밍 시작
    document.getElementById('camOpenBtn').addEventListener('click', startStreaming);

    // 이미지 처리 버튼 클릭 이벤트
    document.getElementById('detectBtn').addEventListener('click', requestProcessing);
});
