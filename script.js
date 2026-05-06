// Create floating particles
const particlesContainer = document.getElementById('particles');
for (let i = 0; i < 50; i++) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    particle.style.left = Math.random() * 100 + '%';
    particle.style.animationDelay = Math.random() * 20 + 's';
    particle.style.animationDuration = (Math.random() * 10 + 15) + 's';
    particlesContainer.appendChild(particle);
}

let demoActive = false;
let statsInterval = null;

// Page navigation function
function showPage(pageName) {
    // Hide all pages
    document.getElementById('home').style.display = 'none';
    document.getElementById('demo').style.display = 'none';
    document.getElementById('about').style.display = 'none';
    
    // Show selected page
    document.getElementById(pageName).style.display = 'flex';
    
    // Scroll to top
    window.scrollTo(0, 0);
}

// Toggle demo camera
function toggleDemo() {
    demoActive = !demoActive;
    const btn = document.getElementById('startBtn');
    const feed = document.getElementById('cameraFeed');
    
    if (demoActive) {
        // Start demo
        btn.innerHTML = '⏹️ Stop Demo';
        btn.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
        feed.innerHTML = '<img src="/video_feed" style="width:100%; height:100%; object-fit:cover;">';
        startStatsPolling();
    } else {
        // Stop demo
        btn.innerHTML = '▶️ Start Demo';
        btn.style.background = 'linear-gradient(135deg, #8b5cf6, #ec4899)';
        
        // Stop camera on server
        fetch('/stop_camera', { method: 'POST' })
            .catch(err => console.error('Stop camera error:', err));
        
        // Reset display
        feed.innerHTML = `
            <div class="camera-placeholder">
                <div style="font-size: 80px;">📷</div>
                <p style="margin-top: 20px; font-size: 18px; color: #8b5cf6;">Camera Stopped</p>
                <p style="color: #666;">Click "Start Demo" to begin again</p>
            </div>
        `;
        
        stopStatsPolling();
    }
}

// Start polling stats from server
function startStatsPolling() {
    statsInterval = setInterval(() => {
        fetch('/stats')
            .then(res => res.json())
            .then(data => {
                // Update gesture text
                document.getElementById('gestureText').textContent = data.gesture || 'None';
                
                // Update FPS bar (multiply by 5 to scale to 100%)
                document.getElementById('fpsFill').style.width = Math.min(data.fps * 5, 100) + '%';
                
                // Update accuracy
                document.getElementById('accuracyFill').style.width = data.accuracy + '%';
                document.getElementById('accuracyValue').textContent = data.accuracy + '%';
            })
            .catch(err => console.error('Stats error:', err));
    }, 100); // Poll every 100ms for smooth updates
}

// Stop polling stats
function stopStatsPolling() {
    if (statsInterval) {
        clearInterval(statsInterval);
        statsInterval = null;
    }
}

// Update settings on server
function updateSettings() {
    const sensitivity = document.getElementById('sensitivitySlider').value;
    const smoothing = document.getElementById('smoothingSlider').value;
    
    fetch('/settings', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json' 
        },
        body: JSON.stringify({ 
            sensitivity: parseInt(sensitivity), 
            smoothing: parseInt(smoothing) 
        })
    })
    .then(res => res.json())
    .then(data => {
        console.log('Settings updated:', data);
    })
    .catch(err => console.error('Settings error:', err));
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (demoActive) {
        fetch('/stop_camera', { method: 'POST' }).catch(() => {});
    }
});

// Log ready state
console.log('🌊 WaveX AI - JavaScript loaded and ready!');