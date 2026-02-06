// ========================================
// YouTube Video Downloader - JavaScript
// ========================================

// Backend API Configuration
const API_BASE_URL = 'http://localhost:3000/api';

// DOM Elements
const videoUrlInput = document.getElementById('videoUrl');
const clearBtn = document.getElementById('clearBtn');
const urlError = document.getElementById('urlError');
const formatSelect = document.getElementById('formatSelect');
const qualitySelect = document.getElementById('qualitySelect');
const downloadBtn = document.getElementById('downloadBtn');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const videoPreview = document.getElementById('videoPreview');
const closePreviewBtn = document.getElementById('closePreview');
const videoThumbnail = document.getElementById('videoThumbnail');
const videoTitle = document.getElementById('videoTitle');
const videoChannel = document.getElementById('videoChannel');
const videoViews = document.getElementById('videoViews');
const videoDate = document.getElementById('videoDate');
const videoDuration = document.getElementById('videoDuration');

// State
let currentVideoId = null;
let isDownloading = false;

// ========================================
// YouTube URL Validation & Parsing
// ========================================

/**
 * Extract video ID from various YouTube URL formats
 */
function extractVideoId(url) {
    const patterns = [
        /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([a-zA-Z0-9_-]{11})/,
        /^([a-zA-Z0-9_-]{11})$/ // Direct video ID
    ];

    for (const pattern of patterns) {
        const match = url.match(pattern);
        if (match) {
            return match[1];
        }
    }

    return null;
}

/**
 * Validate YouTube URL
 */
function validateUrl(url) {
    if (!url || url.trim() === '') {
        return { valid: false, error: 'Please enter a YouTube URL' };
    }

    const videoId = extractVideoId(url);
    if (!videoId) {
        return { valid: false, error: 'Invalid YouTube URL. Please check and try again.' };
    }

    return { valid: true, videoId };
}

// ========================================
// Backend API Integration
// ========================================

/**
 * Fetch video metadata from backend
 */
async function fetchVideoMetadata(videoId) {
    try {
        const response = await fetch(`${API_BASE_URL}/video-info`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ videoId })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to fetch video information');
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching metadata:', error);
        throw error;
    }
}

/**
 * Download video from backend
 */
async function downloadVideo(videoId, format, quality) {
    try {
        updateProgress(10, 'Connecting to server...');

        const response = await fetch(`${API_BASE_URL}/download`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ videoId, format, quality })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Download failed');
        }

        updateProgress(50, 'Downloading video...');

        // Get filename from Content-Disposition header
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'video.mp4';
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="(.+)"/);
            if (filenameMatch) {
                filename = filenameMatch[1];
            }
        }

        updateProgress(80, 'Processing download...');

        // Get the blob
        const blob = await response.blob();

        updateProgress(95, 'Saving file...');

        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();

        // Cleanup
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        return {
            success: true,
            message: 'Video downloaded successfully!'
        };
    } catch (error) {
        console.error('Download error:', error);
        throw error;
    }
}

// ========================================
// UI Update Functions
// ========================================

function showError(message) {
    urlError.textContent = message;
    urlError.classList.add('visible');
    videoUrlInput.parentElement.style.borderColor = 'rgba(255, 77, 77, 0.5)';
}

function hideError() {
    urlError.classList.remove('visible');
    videoUrlInput.parentElement.style.borderColor = 'transparent';
}

function showPreview(metadata) {
    videoThumbnail.src = metadata.thumbnail;
    videoTitle.textContent = metadata.title;
    videoChannel.textContent = metadata.channel;
    videoViews.textContent = metadata.views + ' views';
    videoDate.textContent = metadata.uploadDate;
    videoDuration.textContent = metadata.duration;

    videoPreview.classList.add('visible');
}

function hidePreview() {
    videoPreview.classList.remove('visible');
}

function updateProgress(percentage, message) {
    progressFill.style.width = percentage + '%';
    progressText.textContent = message;
}

function setDownloadingState(downloading) {
    isDownloading = downloading;

    if (downloading) {
        downloadBtn.classList.add('loading');
        progressContainer.classList.add('visible');
        videoUrlInput.disabled = true;
        formatSelect.disabled = true;
        qualitySelect.disabled = true;
    } else {
        downloadBtn.classList.remove('loading');
        videoUrlInput.disabled = false;
        formatSelect.disabled = false;
        qualitySelect.disabled = false;
    }
}

// ========================================
// Event Handlers
// ========================================

// Input change handler
videoUrlInput.addEventListener('input', (e) => {
    const value = e.target.value;

    // Show/hide clear button
    if (value.length > 0) {
        clearBtn.classList.add('visible');
    } else {
        clearBtn.classList.remove('visible');
        hideError();
        hidePreview();
    }

    // Clear error on input
    if (urlError.classList.contains('visible')) {
        hideError();
    }
});

// Clear button handler
clearBtn.addEventListener('click', () => {
    videoUrlInput.value = '';
    clearBtn.classList.remove('visible');
    hideError();
    hidePreview();
    currentVideoId = null;
});

// URL validation on blur
videoUrlInput.addEventListener('blur', async () => {
    const url = videoUrlInput.value.trim();

    if (url === '') {
        hidePreview();
        return;
    }

    const validation = validateUrl(url);

    if (!validation.valid) {
        showError(validation.error);
        hidePreview();
        return;
    }

    hideError();
    currentVideoId = validation.videoId;

    // Fetch and show video preview
    try {
        const metadata = await fetchVideoMetadata(currentVideoId);
        showPreview(metadata);
    } catch (error) {
        showError('Failed to load video information. Make sure the backend server is running.');
        console.error('Error fetching metadata:', error);
    }
});

// Close preview button
closePreviewBtn.addEventListener('click', () => {
    hidePreview();
});

// Download button handler
downloadBtn.addEventListener('click', async () => {
    if (isDownloading) return;

    const url = videoUrlInput.value.trim();
    const validation = validateUrl(url);

    if (!validation.valid) {
        showError(validation.error);
        return;
    }

    hideError();

    const format = formatSelect.value;
    const quality = qualitySelect.value;

    try {
        setDownloadingState(true);
        updateProgress(0, 'Preparing download...');

        const result = await downloadVideo(validation.videoId, format, quality);

        if (result.success) {
            updateProgress(100, result.message);

            // Show success message and reset after delay
            setTimeout(() => {
                progressContainer.classList.remove('visible');
                setDownloadingState(false);
                updateProgress(0, 'Preparing download...');
            }, 3000);
        }
    } catch (error) {
        showError('Download failed. Make sure the backend server is running.');
        console.error('Download error:', error);
        setDownloadingState(false);
        progressContainer.classList.remove('visible');
    }
});

// Format change handler - Update quality options based on format
formatSelect.addEventListener('change', (e) => {
    const format = e.target.value;

    if (format === 'mp3') {
        // For audio, show bitrate options
        qualitySelect.innerHTML = `
            <option value="highest">Highest Quality</option>
            <option value="320kbps">320 kbps</option>
            <option value="256kbps">256 kbps</option>
            <option value="192kbps">192 kbps</option>
            <option value="128kbps">128 kbps</option>
        `;
    } else {
        // For video, show resolution options
        qualitySelect.innerHTML = `
            <option value="highest">Highest Available</option>
            <option value="1080p">1080p (Full HD)</option>
            <option value="720p">720p (HD)</option>
            <option value="480p">480p (SD)</option>
            <option value="360p">360p</option>
        `;
    }
});

// Enter key to trigger download
videoUrlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !isDownloading) {
        downloadBtn.click();
    }
});

// ========================================
// Initialization
// ========================================

console.log('YouTube Video Downloader initialized');
console.log('✅ Backend API configured at:', API_BASE_URL);
console.log('Make sure the backend server is running: npm start');

// Add paste event listener for convenience
videoUrlInput.addEventListener('paste', async (e) => {
    // Small delay to let paste complete
    setTimeout(async () => {
        const url = videoUrlInput.value.trim();
        const validation = validateUrl(url);

        if (validation.valid) {
            clearBtn.classList.add('visible');
            currentVideoId = validation.videoId;

            try {
                const metadata = await fetchVideoMetadata(currentVideoId);
                showPreview(metadata);
                hideError();
            } catch (error) {
                showError('Failed to load video information. Make sure the backend server is running.');
            }
        }
    }, 100);
});
