import os
import yt_dlp
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Path to the cookies.txt file
COOKIES_FILE = 'cookies.txt'  # Replace with the actual path

# reCAPTCHA secret key (replace with your actual secret key)
RECAPTCHA_SECRET_KEY = '3edqwfyutgkmjnhbgvrfedwsq'

# Function to verify reCAPTCHA response
def verify_recaptcha(response_token):
    payload = {
        'secret': RECAPTCHA_SECRET_KEY,
        'response': response_token
    }
    recaptcha_url = 'https://www.google.com/recaptcha/api/siteverify'
    response = requests.post(recaptcha_url, data=payload)
    result = response.json()
    return result.get('success', False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/count', methods=['POST'])
def count_videos():
    # Get the video URL and CAPTCHA response from the request
    video_url = request.json.get('url')
    recaptcha_response = request.json.get('recaptcha')

    # Verify reCAPTCHA response
    if not verify_recaptcha(recaptcha_response):
        return jsonify({'success': False, 'message': 'Invalid CAPTCHA'}), 400

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
    # Get the video URL and CAPTCHA response from the request
    video_url = request.json.get('url')
    recaptcha_response = request.json.get('recaptcha')

    # Verify reCAPTCHA response
    if not verify_recaptcha(recaptcha_response):
        return jsonify({'success': False, 'message': 'Invalid CAPTCHA'}), 400

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
