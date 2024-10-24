import os
import subprocess
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
YT_DLP_PATH = r'yt-dlp.exe'  # Update this to your actual yt-dlp.exe location

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/count', methods=['POST'])
def count_videos():
    video_url = request.json.get('url')
    command = [YT_DLP_PATH, '--flat-playlist', '--dump-single-json', video_url]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        playlist_info = json.loads(result.stdout)
        total_videos = len(playlist_info['entries']) if isinstance(playlist_info, dict) and 'entries' in playlist_info else 1

        return jsonify({'success': True, 'totalVideos': total_videos})

    except subprocess.CalledProcessError as e:
        return jsonify({'success': False, 'message': str(e)})
    except json.JSONDecodeError:
        return jsonify({'success': False, 'message': 'Failed to decode JSON response from yt-dlp.'})

@app.route('/download', methods=['POST'])
def download_videos():
    video_url = request.json.get('url')
    total_videos = request.json.get('totalVideos')
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    video_folder = os.path.join(os.path.expanduser('~'), 'Downloads', f'YouTube Downloads {timestamp}')

    # Ensure the video folder exists
    os.makedirs(video_folder, exist_ok=True)

    # Start downloading all videos at once
    download_command = [YT_DLP_PATH, '-o', os.path.join(video_folder, '%(title)s.%(ext)s'), video_url]

    try:
        subprocess.run(download_command, check=True)
        return jsonify({'success': True})

    except subprocess.CalledProcessError as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
