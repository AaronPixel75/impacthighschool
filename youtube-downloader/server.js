const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Ensure downloads directory exists
const downloadsDir = path.join(__dirname, 'downloads');
if (!fs.existsSync(downloadsDir)) {
    fs.mkdirSync(downloadsDir);
}

// Find yt-dlp binary
const ytDlpBinary = path.join(__dirname, 'node_modules', 'yt-dlp-exec', 'bin', 'yt-dlp.exe');
console.log('Using yt-dlp binary at:', ytDlpBinary);

// ========================================
// API Endpoints
// ========================================

app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', message: 'Server is running with temp-file download strategy' });
});

app.post('/api/video-info', async (req, res) => {
    try {
        const { videoId } = req.body;
        if (!videoId) return res.status(400).json({ error: 'Video ID is required' });

        const videoUrl = `https://www.youtube.com/watch?v=${videoId}`;
        console.log(`Fetching metadata for: ${videoUrl}`);

        // Use Android client to bypass 429/Bot detection
        // And specify Node.js runtime explicit path
        const args = [
            videoUrl,
            '--dump-single-json',
            '--no-playlist',
            '--no-check-certificates',
            '--extractor-args', 'youtube:player_client=android',
            '--force-ipv4',
            '--js-runtimes', `node:"${process.execPath}"`
        ];

        const output = await runYtDlp(args);
        const meta = JSON.parse(output);

        // Map output
        const formats = meta.formats || [];
        const availableQualities = [...new Set(
            formats
                .filter(f => f.format_note && f.ext === 'mp4')
                .map(f => f.format_note)
        )];

        const duration = meta.duration;
        const minutes = Math.floor(duration / 60);
        const seconds = duration % 60;
        const formattedDuration = `${minutes}:${seconds.toString().padStart(2, '0')}`;

        res.json({
            id: videoId,
            title: meta.title,
            channel: meta.uploader,
            thumbnail: meta.thumbnail,
            duration: formattedDuration,
            views: meta.view_count ? meta.view_count.toLocaleString() : 'Unknown',
            uploadDate: meta.upload_date || 'Unknown',
            availableFormats: ['mp4', 'webm', 'mp3'],
            availableQualities: availableQualities.length > 0 ? availableQualities : ['Highest', '1080p', '720p', '480p']
        });

    } catch (error) {
        console.error('Error fetching video info:', error);
        res.status(500).json({
            error: 'Failed to fetch video information',
            details: error.message
        });
    }
});

app.post('/api/download', async (req, res) => {
    const { videoId, format, quality } = req.body;
    if (!videoId) return res.status(400).json({ error: 'Video ID is required' });

    const videoUrl = `https://www.youtube.com/watch?v=${videoId}`;
    const timestamp = Date.now();
    const tempFilename = `download-${videoId}-${timestamp}.${format === 'mp3' ? 'mp3' : 'mp4'}`;
    const tempFilePath = path.join(downloadsDir, tempFilename);

    console.log(`Starting download to temp file: ${tempFilePath}`);

    // Basic args
    const args = [
        videoUrl,
        '-o', tempFilePath,
        '--no-playlist',
        '--no-check-certificates',
        // Use Android client to bypass 429/Bot detection
        '--extractor-args', 'youtube:player_client=android',
        '--extractor-args', 'youtube:player_skip=webpage,configs,js',
        // Force IPv4 to avoid common IPv6 blocks
        '--force-ipv4',
        // Explicitly pass Node.js path for JS interpretation
        '--js-runtimes', `node:"${process.execPath}"`,
        '--retries', '10',
        '--fragment-retries', '10'
    ];

    // Format selection
    if (format === 'mp3') {
        args.push('-x', '--audio-format', 'mp3');
    } else if (format === 'webm') {
        args.push('-f', `bestvideo[ext=webm]+bestaudio/best[ext=webm]`);
    } else {
        // MP4
        if (quality === 'highest' || !quality) {
            args.push('-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best');
        } else {
            const height = parseInt(quality.replace('p', ''));
            if (!isNaN(height)) {
                args.push('-f', `bestvideo[height<=${height}][ext=mp4]+bestaudio[ext=m4a]/best[height<=${height}][ext=mp4]/best`);
            } else {
                args.push('-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best');
            }
        }
    }

    try {
        await runYtDlp(args);

        console.log('Download complete. Sending file to client...');

        // Get actual filename (yt-dlp might rename if converting)
        // Check if file exists, or search for files matching the pattern
        // yt-dlp might add extension, but we forced -o with extension

        if (fs.existsSync(tempFilePath)) {
            res.download(tempFilePath, (err) => {
                if (err) {
                    console.error('Error sending file:', err);
                }
                // Cleanup after send
                fs.unlinkSync(tempFilePath);
            });
        } else {
            throw new Error('Downloaded file not found on server');
        }

    } catch (error) {
        console.error('Download failed:', error);
        res.status(500).json({ error: 'Download failed', details: error.message });

        // Cleanup if partial file exists
        if (fs.existsSync(tempFilePath)) {
            fs.unlinkSync(tempFilePath);
        }
    }
});

// Helper to run yt-dlp
function runYtDlp(args) {
    return new Promise((resolve, reject) => {
        console.log('Spawning:', ytDlpBinary, args.join(' '));
        const child = spawn(ytDlpBinary, args, { windowsHide: true });

        let stdout = '';
        let stderr = '';

        child.stdout.on('data', (data) => {
            stdout += data.toString();
        });

        child.stderr.on('data', (data) => {
            const msg = data.toString();
            stderr += msg;
            if (msg.includes('ERROR')) console.error('yt-dlp stderr:', msg);
        });

        child.on('close', (code) => {
            if (code !== 0) {
                reject(new Error(`yt-dlp exited with ${code}: ${stderr}`));
            } else {
                resolve(stdout);
            }
        });
    });
}

app.listen(PORT, () => {
    console.log(`🚀 Final Robust Server running on http://localhost:${PORT}`);
});
