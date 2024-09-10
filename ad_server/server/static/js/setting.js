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
        const videoFeed = document.getElementById('videoFeed');
        videoFeed.src = "/static/imgs/ImageIcon.png";
    }

    // 카메라 열기 버튼 클릭 시 스트리밍을 시작하는 함수
    function startStreaming() {
        const selectedCamera = document.getElementById('cameraSelect').value;
        const videoFeed = document.getElementById('videoFeed');
        if (selectedCamera !== "") {
            // 기존 이미지 소스 제거
            videoFeed.src = ""; // 이전 이미지나 스트림 해제
            
            videoFeed.src = `http://localhost:8899/video_feed?camera_index=${selectedCamera}`;
            videoFeed.onerror = () => {
                alert("Failed to load video stream. Please check the camera.");
            };

        } else {
            alert("Please select a camera.");
        }
    }

    // HSV 추출 관련
    const toggleButton = document.getElementById('toggleButton');
    const statusIndicator = document.getElementById('statusIndicator');
    let isToolActive = false;
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const videoFeed = document.getElementById('videoFeed');

    // 펜 모양 버튼 클릭 시 기능 활성화/비활성화
    toggleButton.addEventListener('click', function() {
        isToolActive = !isToolActive;
        toggleButton.classList.toggle('active', isToolActive);
        toggleButton.innerHTML = isToolActive ? '<i class="bi bi-pencil-fill"></i>' : '<i class="bi bi-pencil"></i>';
        statusIndicator.style.color = isToolActive ? 'red' : 'green';
        statusIndicator.textContent = isToolActive ? 'Stopped' : 'Live';

        if (isToolActive) {
            // 실시간 영상을 캔버스로 캡처하고 실시간 스트림 중지
            stopStreamingAndShowFrame();
        } else {
            // 실시간 영상으로 다시 전환
            startStreaming();  // 스트리밍 재시작
        }
    });

    // 실시간 스트리밍 중지하고 서버에서 받은 이미지를 캔버스에 표시하는 함수
    function stopStreamingAndShowFrame() {
        const selectedCamera = document.getElementById('cameraSelect').value;
        const videoFeed = document.getElementById('videoFeed');
        
        // 실시간 스트림을 중지
        const stream = videoFeed.srcObject;
        if (stream) {
            const tracks = stream.getTracks();
            tracks.forEach(track => track.stop()); // 모든 트랙을 중지
            videoFeed.srcObject = null; // 비디오 소스를 해제
        }
        
        // videoFeed.src = ""; // 이전 이미지나 스트림 해제

        // FastAPI 서버에서 이미지를 가져와서 비디오 피드에 표시
        fetch(`http://localhost:8899/image_feed?camera_index=${selectedCamera}`)
            .then(response => response.blob())  // 이미지 데이터를 Blob 형식으로 받음
            .then(blob => {
                const imageURL = URL.createObjectURL(blob);  // Blob 데이터를 URL로 변환
                videoFeed.src = imageURL;  // 비디오 대신 서버에서 받은 이미지로 전환
        
                // 이미지가 정상적으로 로드되었는지 확인
                videoFeed.onload = () => {
                    console.log("Image loaded successfully.");
                };
        
                // 이미지 로드에 실패했을 경우
                videoFeed.onerror = () => {
                    console.error("Failed to load the image.");
                };
            })
            .catch(error => {
                console.error("Error fetching image from server:", error);
        });

        alert("펜 모드 활성화")
    }

    // 비디오 피드가 준비되었을 때 이벤트 추가
    videoFeed.addEventListener('canplay', function() {
        videoFeed.addEventListener('click', function(event) {
            if (!isToolActive) return;  // HSV 추출 도구가 활성화되지 않았으면 실행 안 함

            const rect = videoFeed.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;

            if (videoFeed.readyState >= videoFeed.HAVE_CURRENT_DATA) {
                canvas.width = videoFeed.videoWidth;
                canvas.height = videoFeed.videoHeight;
                try {
                    // 비디오 프레임을 캔버스로 복사
                    ctx.drawImage(videoFeed, 0, 0, canvas.width, canvas.height);
                } catch (error) {
                    console.error("Error drawing image to canvas:", error);
                    return;
                }

                const imageData = ctx.getImageData(x, y, 1, 1).data;
                const r = imageData[0];
                const g = imageData[1];
                const b = imageData[2];

                const hsv = rgbToHsv(r, g, b);
                displayHSV(hsv[0], hsv[1], hsv[2]);
            } else {
                console.error("Video not ready for processing.");
            }
        });
    });

    // RGB를 HSV로 변환하는 함수
    function rgbToHsv(r, g, b) {
        r /= 255;
        g /= 255;
        b /= 255;
        const max = Math.max(r, g, b), min = Math.min(r, g, b);
        const delta = max - min;
        let h, s, v = max;

        if (delta === 0) h = 0;
        else if (max === r) h = ((g - b) / delta + (g < b ? 6 : 0)) % 6;
        else if (max === g) h = (b - r) / delta + 2;
        else h = (r - g) / delta + 4;

        h = Math.round(h * 60);
        s = max === 0 ? 0 : delta / max;
        s = Math.round(s * 100);
        v = Math.round(v * 100);

        return [h, s, v];
    }

    // HSV 값을 표시하는 함수
    function displayHSV(h, s, v) {
        let hsvDisplay = document.getElementById('hsvDisplay');
        if (!hsvDisplay) {
            hsvDisplay = document.createElement('div');
            hsvDisplay.id = 'hsvDisplay';
            const configSection = document.querySelector('.col-md-12.mb-4');
            configSection.appendChild(hsvDisplay);
        }
        hsvDisplay.innerHTML = `H: ${h}, S: ${s}, V: ${v}`;
    }

    // 화면 모드 변경 처리
    const videoSection = document.getElementById('videoSection');  // 실시간 카메라 구역
    const processedImageSection = document.getElementById('processedImageSection');  // 처리된 이미지 구역
    const processedImage = document.getElementById('processedImage');  // 처리된 이미지

    document.getElementById('viewModeSelect').addEventListener('change', function() {
        const selectedMode = this.value;

        if (selectedMode === '1|2') {
            resetSections(); // 기본 모드로 돌아갈 때 리셋
            videoSection.hidden = false;
            processedImageSection.hidden = false;
        } else if (selectedMode === '1') {
            resetSections(); // 리셋 후 1번 모드 적용
            videoSection.hidden = false;
            processedImageSection.hidden = true;
            applyFullscreen(videoSection, videoFeed, '1500px'); // 부모와 이미지 모두 크게
        } else if (selectedMode === '2') {
            resetSections(); // 리셋 후 2번 모드 적용
            videoSection.hidden = true;
            processedImageSection.hidden = false;
            applyFullscreen(processedImageSection, processedImage, '1500px'); // 부모와 이미지 모두 크게
        }
    });

    // 섹션 크기와 스타일을 리셋하는 함수
    function resetSections() {
        videoFeed.classList.remove('fullscreen');
        processedImage.classList.remove('fullscreen');
        videoSection.style.width = "";  // 부모 크기 기본값으로 리셋
        videoSection.style.maxWidth = "";  // 기본값으로 리셋
        processedImageSection.style.width = "";  // 부모 크기 기본값으로 리셋
        processedImageSection.style.maxWidth = "";  // 기본값으로 리셋
    }

    // 특정 섹션을 풀스크린으로 적용하는 함수
    function applyFullscreen(section, image, maxWidth) {
        image.classList.add('fullscreen'); // 이미지 크게
        section.style.width = "100%";  // 부모 요소의 너비를 100%로 설정
        section.style.maxWidth = maxWidth;  // 최대 너비를 설정
    }

    // 테이블 열 데이터 가져오기
    function collectTableData() {
        const tableBody = document.getElementById('configTableBody');
        const rows = tableBody.querySelectorAll('tr');
        const setting_list = [];

        rows.forEach((row, index) => {
            const margin = row.querySelector('input[name="margin"]').value;
            const lower_bound = row.querySelector('input[name="lower_bound"]').value;
            const upper_bound = row.querySelector('input[name="upper_bound"]').value;

            setting_list.push({
                rowIndex: index + 1,
                margin: parseFloat(margin),
                lower_bound: parseFloat(lower_bound),
                upper_bound: parseFloat(upper_bound)
            });
        });

        return setting_list;
    }

    // 이미지 처리 요청
    function requestProcessing() {
        const tableData = collectTableData();

        fetch('http://localhost:8899/image_processing', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(tableData)
        })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
                alert('Image processed successfully.');
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error occurred while processing the image.');
            });
    }

    // Row 추가 및 삭제
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
