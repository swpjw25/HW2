const uploadZone = document.getElementById('upload-zone');
const fileInput = document.getElementById('file-input');
const imagePreview = document.getElementById('image-preview');
const uploadContent = document.getElementById('upload-content');
const evaluateBtn = document.getElementById('evaluate-btn');
const resultsPanel = document.getElementById('results-panel');

let selectedFile = null;

// Drag and drop events
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    uploadZone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults (e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    uploadZone.addEventListener(eventName, () => uploadZone.classList.add('dragover'), false);
});

['dragleave', 'drop'].forEach(eventName => {
    uploadZone.addEventListener(eventName, () => uploadZone.classList.remove('dragover'), false);
});

uploadZone.addEventListener('drop', handleDrop, false);
uploadZone.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', function() {
    if (this.files && this.files[0]) {
        handleFile(this.files[0]);
    }
});

function handleDrop(e) {
    let dt = e.dataTransfer;
    let files = dt.files;
    if (files.length) {
        handleFile(files[0]);
    }
}

function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        alert("Please upload an image file.");
        return;
    }
    selectedFile = file;
    
    // Show preview
    let reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onloadend = function() {
        imagePreview.src = reader.result;
        imagePreview.style.display = 'block';
        uploadContent.style.opacity = '0';
        evaluateBtn.disabled = false;
    }
}

evaluateBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    evaluateBtn.classList.add('btn-loading');
    evaluateBtn.disabled = true;
    resultsPanel.classList.add('hidden');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch('/evaluate', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        displayResults(data);
    } catch (error) {
        console.error('Error detail:', error);
        if (error.message.includes('fetch')) {
            alert('❌ 서버에 연결할 수 없습니다. \n1. 터미널에서 "python main.py"가 실행 중인지 확인하세요.\n2. http://localhost:8000 으로 접속했는지 확인하세요.');
        } else {
            alert(`❌ 평가 도중 에러가 발생했습니다: \n${error.message}`);
        }
    } finally {
        evaluateBtn.classList.remove('btn-loading');
        evaluateBtn.disabled = false;
    }
});

function displayResults(data) {
    const { score, feedback, improvements } = data;
    
    document.getElementById('score-value').innerText = 0;
    document.getElementById('feedback-text').innerText = feedback;
    
    const impList = document.getElementById('improvements-list');
    impList.innerHTML = '';
    
    improvements.forEach(imp => {
        const li = document.createElement('li');
        li.innerText = imp;
        impList.appendChild(li);
    });

    resultsPanel.classList.remove('hidden');

    // Color code the score circle based on score
    const circle = document.getElementById('score-circle-path');
    let color = '#ec4899'; // Default pinkish
    if (score >= 80) color = '#10b981'; // Green
    else if (score >= 60) color = '#f59e0b'; // Yellow
    
    circle.style.stroke = color;

    // Animate score
    animateValue('score-value', 0, score, 1500);
    setTimeout(() => {
        circle.style.strokeDasharray = `${score}, 100`;
    }, 100);
}

function animateValue(id, start, end, duration) {
    const obj = document.getElementById(id);
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerHTML = Math.floor(progress * (end - start) + start);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            obj.innerHTML = end;
        }
    };
    window.requestAnimationFrame(step);
}
