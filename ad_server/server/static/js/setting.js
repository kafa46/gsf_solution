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

    // 이미지 처리
    function processedImage() {
        fetch('http://localhost:8899/processed_image')
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
    document.getElementById('detectBtn').addEventListener('click', processedImage);
});
