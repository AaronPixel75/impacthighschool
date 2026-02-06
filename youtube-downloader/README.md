# YouTube Video Downloader

A modern, beautiful web application for downloading YouTube videos with support for multiple formats and quality options.

## Features

- 🎨 **Beautiful Modern UI** - Glassmorphism design with animated gradients
- ⚡ **Fast Downloads** - Powered by ytdl-core
- 🎬 **Multiple Formats** - MP4, MP3, WebM support
- 🎯 **Quality Options** - Download in 1080p, 720p, 480p, 360p, or highest available
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🔍 **Video Preview** - See video details before downloading

## Prerequisites

- Node.js (v16 or higher)
- npm (comes with Node.js)
- Modern web browser (Chrome, Firefox, Edge, Safari)

## Installation

1. **Navigate to the project directory**
   ```bash
   cd youtube-downloader
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

   This will install:
   - Express (web server)
   - CORS (cross-origin resource sharing)
   - ytdl-core (YouTube download library)

## Usage

### Starting the Backend Server

1. **Start the server**
   ```bash
   npm start
   ```

2. **Verify server is running**
   - You should see: `🚀 YouTube Downloader Backend Server running on http://localhost:3000`
   - The server will be accessible at `http://localhost:3000`

### Using the Application

1. **Open the frontend**
   - Open `index.html` in your web browser
   - Or double-click the file to open it

2. **Download a video**
   - Paste a YouTube URL into the input field
   - Wait for the video preview to load
   - Select your preferred format (MP4, MP3, WebM)
   - Choose quality level
   - Click "Download Video"
   - The video will download to your browser's default download location

## API Endpoints

### GET /api/health
Health check endpoint to verify server is running.

**Response:**
```json
{
  "status": "ok",
  "message": "Server is running"
}
```

### POST /api/video-info
Fetch video metadata.

**Request Body:**
```json
{
  "videoId": "dQw4w9WgXcQ"
}
```

**Response:**
```json
{
  "id": "dQw4w9WgXcQ",
  "title": "Video Title",
  "channel": "Channel Name",
  "thumbnail": "https://...",
  "duration": "3:32",
  "views": "1,234,567",
  "uploadDate": "2009-10-25",
  "availableFormats": ["mp4", "webm", "mp3"],
  "availableQualities": ["1080p", "720p", "480p", "360p"]
}
```

### POST /api/download
Download video.

**Request Body:**
```json
{
  "videoId": "dQw4w9WgXcQ",
  "format": "mp4",
  "quality": "720p"
}
```

**Response:**
- Streams the video file directly to the client

## Project Structure

```
youtube-downloader/
├── index.html          # Frontend HTML
├── styles.css          # Frontend styles
├── script.js           # Frontend JavaScript
├── server.js           # Backend Express server
├── package.json        # Node.js dependencies
├── .gitignore          # Git ignore rules
├── README.md           # This file
└── downloads/          # Downloaded files (created automatically)
```

## Troubleshooting

### Server won't start
- Make sure Node.js is installed: `node --version`
- Make sure dependencies are installed: `npm install`
- Check if port 3000 is already in use

### Downloads fail
- Verify the YouTube URL is valid
- Check your internet connection
- Some videos may be restricted or unavailable
- Age-restricted videos may not work

### CORS errors
- Make sure the backend server is running
- Verify you're accessing the frontend via the same protocol (file:// or http://)

## Legal Notice

⚠️ **Important**: This tool is for educational purposes only. 

YouTube's Terms of Service prohibit unauthorized downloading of content. Only download videos that:
- You have uploaded yourself
- Are explicitly licensed for download (Creative Commons)
- You have written permission to download

Users are responsible for complying with all applicable laws and YouTube's Terms of Service.

## License

MIT License - Feel free to use and modify for educational purposes.

## Support

For issues or questions, please check:
- YouTube video is publicly accessible
- Backend server is running
- Browser console for error messages
