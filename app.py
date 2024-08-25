from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
from PIL import Image
import zipfile
import shutil

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

def download_image(image_url, save_path):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f'Downloaded: {save_path}')
    except requests.exceptions.RequestException as e:
        print(f'Failed to download {image_url}: {e}')

def process_episode(base_url, episode_number, save_directory):
    webpage_url = f'{base_url}/chapter-{episode_number}/'
    print(f'Processing {webpage_url}...')

    episode_dir = f'Episode_{episode_number}'
    save_directory_episode = os.path.join(save_directory, episode_dir)
    os.makedirs(save_directory_episode, exist_ok=True)

    try:
        response = requests.get(webpage_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f'Failed to fetch the webpage: {e}')
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    image_tags = soup.find_all('img')

    if not image_tags:
        print(f'No images found for episode {episode_number}.')
        return None

    image_paths = []
    image_count = 1

    for img in image_tags:
        img_url = img.get('src')
        if img_url:
            full_img_url = urljoin(webpage_url, img_url)
            img_name = f'E{episode_number}IMG{image_count}.jpg'
            save_path = os.path.join(save_directory_episode, img_name)
            download_image(full_img_url, save_path)
            image_paths.append(save_path)
            image_count += 1

    if image_paths:
        images = [Image.open(img_path).convert('RGB') for img_path in image_paths]
        pdf_path = os.path.join(save_directory, f'Episode_{episode_number}.pdf')
        images[0].save(pdf_path, save_all=True, append_images=images[1:])
        print(f'PDF created: {pdf_path}')
        return pdf_path
    return None

@app.route('/download_manga', methods=['POST'])
def download_manga():
    data = request.json

    base_url = data.get('base_url')
    start_chapter = data.get('start_chapter')
    end_chapter = data.get('end_chapter')

    if not base_url or not start_chapter or not end_chapter:
        return jsonify({"error": "Invalid input. Please provide all required fields."}), 400
    
    try:
        start_chapter = int(start_chapter)
        end_chapter = int(end_chapter)
    except ValueError:
        return jsonify({"error": "Chapter numbers must be integers."}), 400

    save_directory = 'manga_downloads'
    os.makedirs(save_directory, exist_ok=True)

    file_list = []
    for episode_number in range(start_chapter, end_chapter + 1):
        pdf_path = process_episode(base_url, episode_number, save_directory)
        if pdf_path:
            file_list.append({
                'episode': f'Episode {episode_number}',
                'url': f'/static/{os.path.basename(pdf_path)}'
            })

    return jsonify({"status": "Download started", "files": file_list}), 200

@app.route('/download_all_files', methods=['POST'])
def download_all_files():
    data = request.json
    start_chapter = data.get('start_chapter')
    end_chapter = data.get('end_chapter')

    save_directory = 'manga_downloads'
    zip_filename = 'all_files.zip'
    zip_filepath = os.path.join(save_directory, zip_filename)

    with zipfile.ZipFile(zip_filepath, 'w') as zipf:
        for episode_number in range(int(start_chapter), int(end_chapter) + 1):
            pdf_path = os.path.join(save_directory, f'Episode_{episode_number}.pdf')
            if os.path.exists(pdf_path):
                zipf.write(pdf_path, os.path.basename(pdf_path))

    return jsonify({"zip_url": f'/static/{zip_filename}'}), 200

@app.route('/download_selected_files', methods=['POST'])
def download_selected_files():
    data = request.json
    files = data.get('files', [])
    save_directory = 'manga_downloads'
    zip_filename = 'selected_files.zip'
    zip_filepath = os.path.join(save_directory, zip_filename)

    with zipfile.ZipFile(zip_filepath, 'w') as zipf:
        for file_url in files:
            file_path = os.path.join(save_directory, os.path.basename(file_url))
            if os.path.exists(file_path):
                zipf.write(file_path, os.path.basename(file_path))

    return jsonify({"zip_url": f'/static/{zip_filename}'}), 200

@app.route('/clear_database', methods=['POST'])
def clear_database():
    save_directory = 'manga_downloads'
    if os.path.exists(save_directory):
        shutil.rmtree(save_directory)
    return '', 204

@app.route('/static/<filename>')
def serve_file(filename):
    return send_from_directory('manga_downloads', filename)

if __name__ == '__main__':
    app.run(debug=True)
