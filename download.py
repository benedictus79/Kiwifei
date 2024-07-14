import yt_dlp
import requests
from login import kiwifysession
from utils import SilentLogger, os, shorten_folder_name


def download_files(lesson_folder, name, url):
  headers = kiwifysession.headers
  response = requests.get(url, headers=headers)
  lesson_folder = shorten_folder_name(os.path.join(lesson_folder, name))
  with open(lesson_folder, 'wb') as f:
    f.write(response.content)


def save_html(content_folder, html):
  file_path = shorten_folder_name(os.path.join(content_folder, 'texto.html'))
  if not os.path.exists(file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
      file.write(str(html))


def download_with_ytdlp(output_folder, media, session=None):
  ydl_opts = {
    'logger': SilentLogger(media, f'{output_folder}.%(ext)s'),
    'merge_output_format': 'mp4',
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': f'{output_folder}.%(ext)s',
    'quiet': True,
    'continuedl': True,
    'no_progress': True,
    'no_overwrites': True,
    'windows_filenames': True,
    'retries': 50,
    'trim_file_name': 249,
    'fragment_retries': 50,
    'extractor_retries': 50,
    'file_access_retries': 50,
    'concurrent_fragment_downloads': 10,
  }
  if session:
    ydl_opts['http_headers'] = {'referer': session.headers['referer']}
    ydl_opts['http_headers'] = session.headers.update({'Upgrade-Insecure-Requests': '1'})
  with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      ydl.download([media])
