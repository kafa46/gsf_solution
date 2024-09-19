document.addEventListener('DOMContentLoaded', function() {
    // State
    let isSaving = false;
    let isToolActive = false;

    // DOM Elements
    const elements = {
        videoFeed: document.getElementById('videoFeed'),
        cameraSelect: document.getElementById('cameraSelect'),
        toggleButton: document.getElementById('toggleButton'),
        statusIndicator: document.getElementById('statusIndicator'),
        hsvDisplay: document.getElementById('hsvDisplay'),
        configHsvDisplay: document.getElementById('configHsvDisplay'),
        hsvRange: document.getElementById('hsvRange'),
        hsvRangeValue: document.getElementById('hsvRangeValue'),
        rowSelect: document.getElementById('rowSelect'),
        autoInputBtn: document.getElementById('autoInputBtn'),
        configTableBody: document.getElementById('configTableBody'),
        videoSection: document.getElementById('videoSection'),
        processedImageSection: document.getElementById('processedImageSection'),
        processedImage: document.getElementById('processedImage'),
        viewModeSelect: document.getElementById('viewModeSelect'),
        savingStatus: document.getElementById('savingStatus')
    };

    // Initialize
    init();

    function init() {
        elements.autoInputBtn.disabled = true;
        elements.hsvDisplay.hidden = true;
        attachEventListeners();
        updateRowSelect();
    }

    function attachEventListeners() {
        elements.toggleButton.addEventListener('click', toggleTool);
        elements.hsvRange.addEventListener('input', updateHsvRangeValue);
        elements.rowSelect.addEventListener('change', handleRowSelect);
        elements.autoInputBtn.addEventListener('click', handleAutoInput);
        elements.configTableBody.addEventListener('click', handleRowRemove);
        elements.viewModeSelect.addEventListener('change', handleViewModeChange);
        
        document.getElementById('refreshBtn').addEventListener('click', refreshCameraList);
        document.getElementById('camOpenBtn').addEventListener('click', startStreaming);
        document.getElementById('addRowBtn').addEventListener('click', addRow);
        document.getElementById('detectBtn').addEventListener('click', requestProcessing);
        document.getElementById('saveStartBtn').addEventListener('click', saveStart);
        document.getElementById('saveStopBtn').addEventListener('click', saveStop);
    }

    // Camera Functions
    function refreshCameraList() {
        if (isSaving) {
            alert("이미지 저장중이므로 다른 동작을 수행하실 수 없습니다.");
            return;
        }

        fetch('http://localhost:8899/available_cameras')
            .then(response => response.json())
            .then(data => {
                elements.cameraSelect.innerHTML = '<option value="">Select a camera</option>';
                data.available_cameras.forEach(cameraIndex => {
                    const option = document.createElement('option');
                    option.value = cameraIndex;
                    option.text = `Camera ${cameraIndex}`;
                    elements.cameraSelect.appendChild(option);
                });
            });
        elements.videoFeed.src = "/static/imgs/ImageIcon.png";
    }

    function startStreaming() {
        if (isSaving) {
            alert("이미지 저장중이므로 다른 동작을 수행하실 수 없습니다.");
            return;
        }

        const selectedCamera = elements.cameraSelect.value;
        if (selectedCamera !== "") {
            elements.videoFeed.src = `http://localhost:8899/video_feed?camera_index=${selectedCamera}`;
            elements.videoFeed.onerror = () => {
                alert("Failed to load video stream. Please check the camera.");
            };
        } else {
            alert("Please select a camera.");
        }
    }

    function stopStreamingAndShowFrame() {
        const selectedCamera = elements.cameraSelect.value;
        const stream = elements.videoFeed.srcObject;
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            elements.videoFeed.srcObject = null;
        }

        fetch(`http://localhost:8899/image_feed?camera_index=${selectedCamera}`)
            .then(response => response.blob())
            .then(blob => {
                const imageURL = URL.createObjectURL(blob);
                elements.videoFeed.src = imageURL;
                elements.videoFeed.onload = enableHsvExtraction;
                elements.videoFeed.onerror = () => console.error("Failed to load the image.");
            })
            .catch(error => console.error("Error fetching image from server:", error));

        alert("펜 모드 활성화");
    }

    // HSV Extraction
    function enableHsvExtraction() {
        elements.videoFeed.removeEventListener('click', extractHsvOnClick);
        elements.videoFeed.addEventListener('click', extractHsvOnClick);
    }

    function extractHsvOnClick(event) {
        const rect = elements.videoFeed.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        const canvas = document.createElement('canvas');
        canvas.width = elements.videoFeed.width;
        canvas.height = elements.videoFeed.height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(elements.videoFeed, 0, 0, canvas.width, canvas.height);

        const pixelData = ctx.getImageData(x, y, 1, 1).data;
        const [r, g, b] = [pixelData[0], pixelData[1], pixelData[2]];

        fetch('http://localhost:8899/rgb2hsv', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ r, g, b })
        })
        .then(response => response.json())
        .then(hsv => {
            elements.hsvDisplay.textContent = `HSV: H(${hsv.h}), S(${hsv.s}), V(${hsv.v})`;
            updateHsvDisplay(hsv.h, hsv.s, hsv.v);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error occurred while converting RGB to HSV.');
        });
    }

    // UI Functions
    function toggleTool() {
        isToolActive = !isToolActive;
        elements.toggleButton.textContent = isToolActive ? 'Stop' : 'Live';
        elements.toggleButton.classList.toggle('btn-danger', isToolActive);
        elements.toggleButton.classList.toggle('btn-primary', !isToolActive);
        elements.statusIndicator.style.color = isToolActive ? 'red' : 'green';
        elements.statusIndicator.textContent = isToolActive ? 'Stopped' : 'Live';
        elements.hsvDisplay.hidden = !isToolActive;

        if (isToolActive) {
            stopStreamingAndShowFrame();
        } else {
            startStreaming();
        }
    }

    function updateHsvRangeValue() {
        elements.hsvRangeValue.textContent = elements.hsvRange.value;
    }

    function updateHsvDisplay(h, s, v) {
        elements.configHsvDisplay.textContent = `HSV: H(${h}), S(${s}), V(${v})`;
        updateRowSelect();
    }

    function updateRowSelect() {
        elements.rowSelect.innerHTML = '<option value="">Select</option>';
        const rows = elements.configTableBody.querySelectorAll('tr');
        rows.forEach((row, index) => {
            const option = document.createElement('option');
            option.value = index + 1;
            option.textContent = `Row ${index + 1}`;
            elements.rowSelect.appendChild(option);
        });
    }

    function handleRowSelect() {
        elements.autoInputBtn.disabled = !this.value;
    }

    function handleAutoInput() {
        const selectedRow = parseInt(elements.rowSelect.value) - 1;
        const range = parseInt(elements.hsvRange.value);
        const hsv = elements.configHsvDisplay.textContent.match(/H\((\d+)\), S\((\d+)\), V\((\d+)\)/);
        
        if (hsv && selectedRow >= 0) {
            const [h, s, v] = [parseInt(hsv[1]), parseInt(hsv[2]), parseInt(hsv[3])];
            const row = elements.configTableBody.querySelectorAll('tr')[selectedRow];
            
            row.querySelector('input[name="lower_h"]').value = Math.max(0, h - range);
            row.querySelector('input[name="lower_s"]').value = Math.max(0, s - range);
            row.querySelector('input[name="lower_v"]').value = Math.max(0, v - range);
            
            row.querySelector('input[name="upper_h"]').value = Math.min(179, h + range);
            row.querySelector('input[name="upper_s"]').value = Math.min(255, s + range);
            row.querySelector('input[name="upper_v"]').value = Math.min(255, v + range);
        }
    }

    function addRow() {
        const rowCount = elements.configTableBody.rows.length + 1;
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td>${rowCount}</td>
            <td><input type="number" class="form-control" name="margin" placeholder="Enter Margin"></td>
            <td>
                <div style="display: flex; gap: 5px;">
                    <input type="number" class="form-control" name="lower_h" placeholder="H" style="width: 100px;">
                    <input type="number" class="form-control" name="lower_s" placeholder="S" style="width: 100px;">
                    <input type="number" class="form-control" name="lower_v" placeholder="V" style="width: 100px;">
                </div>
            </td>
            <td>
                <div style="display: flex; gap: 5px;">
                    <input type="number" class="form-control" name="upper_h" placeholder="H" style="width: 100px;">
                    <input type="number" class="form-control" name="upper_s" placeholder="S" style="width: 100px;">
                    <input type="number" class="form-control" name="upper_v" placeholder="V" style="width: 100px;">
                </div>
            </td>
            <td><button type="button" class="btn btn-outline-danger btn-sm remove-row">삭제</button></td>
        `;
        elements.configTableBody.appendChild(newRow);
        updateRowSelect();
    }

    function handleRowRemove(e) {
        if (e.target.classList.contains('remove-row')) {
            e.target.closest('tr').remove();
            updateRowSelect();
        }
    }

    function handleViewModeChange() {
        const selectedMode = this.value;
        if (selectedMode === '1|2') {
            resetSections();
            showBothSections();
        } else if (selectedMode === '1') {
            resetSections();
            showOnlyVideoSection();
        } else if (selectedMode === '2') {
            resetSections();
            showOnlyProcessedSection();
        }
    }

    function resetSections() {
        [elements.videoSection, elements.processedImageSection].forEach(section => {
            if (section) {
                section.style.width = '';
                section.style.maxWidth = '';
                section.classList.remove('d-none');
                section.classList.remove('col-md-12');
                section.classList.add('col-md-6');
            }
        });
    
        [elements.videoFeed, elements.processedImage].forEach(image => {
            if (image) {
                image.classList.remove('fullscreen');
            }
        });
    }

    
    function showBothSections() {
        elements.videoSection.classList.remove('d-none');
        elements.processedImageSection.classList.remove('d-none');
    }

    function showOnlyVideoSection() {
        elements.videoSection.classList.remove('col-md-6');
        elements.videoSection.classList.add('col-md-12');
        elements.processedImageSection.classList.add('d-none');
        applyFullscreen(elements.videoSection, elements.videoFeed);
    }
    
    function showOnlyProcessedSection() {
        elements.processedImageSection.classList.remove('col-md-6');
        elements.processedImageSection.classList.add('col-md-12');
        elements.videoSection.classList.add('d-none');
        applyFullscreen(elements.processedImageSection, elements.processedImage);
    }

    function applyFullscreen(section, image, maxWidth) {
        image.classList.add('fullscreen');
        section.style.width = "100%";
        section.style.maxWidth = maxWidth;
    }

    // Data Processing
    function collectTableData() {
        const rows = elements.configTableBody.querySelectorAll('tr');
        return Array.from(rows).map((row, index) => ({
            rowIndex: index + 1,
            margin: parseFloat(row.querySelector('input[name="margin"]').value),
            lower_bound: {
                h: parseFloat(row.querySelector('input[name="lower_h"]').value),
                s: parseFloat(row.querySelector('input[name="lower_s"]').value),
                v: parseFloat(row.querySelector('input[name="lower_v"]').value)
            },
            upper_bound: {
                h: parseFloat(row.querySelector('input[name="upper_h"]').value),
                s: parseFloat(row.querySelector('input[name="upper_s"]').value),
                v: parseFloat(row.querySelector('input[name="upper_v"]').value)
            }
        }));
    }

    function requestProcessing() {
        if (isSaving) {
            alert("이미지 저장중이므로 다른 동작을 수행하실 수 없습니다.");
            return;
        }
        
        if (!isToolActive) {
            alert('error : 실시간 영상이 stop 상태인지 확인해주세요');
            return;
        }

        const tableData = collectTableData();
    
        fetch('http://localhost:8899/image_processing', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(tableData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success' || data.status === 'partial_success') {
                processedImages(data.image_paths);
                if (data.alert_message) alert(data.alert_message);
                if (data.failed_detections.length > 0) {
                    console.log('Failed detections for rows:', data.failed_detections);
                }
                alert(`Images processed. Successful: ${data.successful_detections}, Failed: ${data.failed_detections.length}`);
            } else {
                throw new Error('Image processing failed');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('error : 카메라가 Stop 상태인지 확인해 주시고, 값을 정확하게 입력했는지 확인해주세요.');
        });
    }

    function processedImages(imagePaths) {
        const select = document.getElementById('processedImageSelect');
        select.innerHTML = '<option value="default">Select Image</option>';
        select.add(new Option('FULL', 'FULL'));
    
        imagePaths.forEach((path, index) => {
            select.add(new Option(`Image ${index + 1}`, path));
        });
    
        function updateImage(src) {
            const timestamp = new Date().getTime();
            elements.processedImage.src = `${src}?t=${timestamp}`;
        }
    
        if (imagePaths.length > 0) {
            updateImage(`http://localhost:8899${imagePaths[0].replace(/^\./, '')}`);
            select.value = imagePaths[0];
        } else {
            elements.processedImage.src = "/static/imgs/ImageIcon.png";
            select.value = "default";
        }
    
        select.onchange = function() {
            if (this.value === "FULL") {
                updateImage("http://localhost:8899/temp/output/all_crop.png");
            } else if (this.value !== "default") {
                updateImage(`http://localhost:8899${this.value.replace(/^\./, '')}`);
            } else {
                elements.processedImage.src = "/static/imgs/ImageIcon.png";
            }
        };
    }
    
    function saveStart() {
        if (isSaving) {
            alert("저장 중입니다.");
            return;
        }
        fetch('http://localhost:8899/image_save_start')
        .then(response => response.json())
        .then(data => {
            isSaving = true;
            console.log('Save started:', data);
            alert('Image saving started.');
            
            isToolActive = false;
            updateToolState();

            elements.savingStatus.textContent = "현재 이미지 저장 중입니다. 페이지를 끄거나 변경하지 말아주세요.";
            elements.savingStatus.style.display = 'block';
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error occurred while starting image save.');
        });
    }

    function saveStop() {
        fetch('http://localhost:8899/image_save_stop')
            .then(response => response.json())
            .then(data => {
                console.log('Save stopped:', data);
                alert('Image saving stopped.');
                
                elements.savingStatus.style.display = 'none';
                isSaving = false; 
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error occurred while stopping image save.');
            });
    }

    function updateToolState() {
        elements.toggleButton.classList.toggle('active', isToolActive);
        elements.toggleButton.textContent = isToolActive ? 'Stop' : 'Start';
        elements.toggleButton.classList.toggle('btn-danger', isToolActive);
        elements.toggleButton.classList.toggle('btn-primary', !isToolActive);
        elements.statusIndicator.style.color = isToolActive ? 'red' : 'green';
        elements.statusIndicator.textContent = isToolActive ? 'Stopped' : 'Live';
        elements.hsvDisplay.hidden = !isToolActive;
    }
});