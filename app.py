import os
import yt_dlp
from datetime import datetime
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Path to the cookies.txt file
COOKIES_FILE = 'cookies.txt'  # Replace with the actual path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/count', methods=['POST'])
def count_videos():
    video_url = request.json.get('url')

    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'cookies': COOKIES_FILE,  # Use cookies to authenticate
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(video_url, download=False)

        total_videos = len(playlist_info['entries']) if 'entries' in playlist_info else 1

        return jsonify({'success': True, 'totalVideos': total_videos})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/download', methods=['POST'])
def download_videos():
    video_url = request.json.get('url')
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    video_folder = os.path.join(os.path.expanduser('~'), 'Downloads', f'YouTube Downloads {timestamp}')

    # Ensure the video folder exists
    os.makedirs(video_folder, exist_ok=True)

    ydl_opts = {
        'outtmpl': os.path.join(video_folder, '%(title)s.%(ext)s'),
        'cookies': COOKIES_FILE,  # Use cookies to authenticate
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
