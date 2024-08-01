from login import selected_course, kiwifysession
from download import download_files, download_with_ytdlp, save_html
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import clear_folder_name, logger, os, create_folder, shorten_folder_name
from tqdm import tqdm


def check_url_player(lesson_name_media, url):
  if 'https://' not in url:
    url = f'https://d3pjuhbfoxhm7c.cloudfront.net{url}'
    download_with_ytdlp(lesson_name_media, url)
  elif 'vimeo' in url:
    download_with_ytdlp(lesson_name_media, url)


def process_lesson_video(lesson_folder, lesson):
  if lesson.get('video'):
    lesson_name_media = os.path.join(lesson_folder, 'aula')
    url = lesson['video']['stream_link']
    check_url_player(lesson_name_media, url)
  if lesson.get('youtube_video'):
    lesson_name_media = os.path.join(lesson_folder, 'aula')
    url = lesson['youtube_video']
    download_with_ytdlp(lesson_name_media, url)


def process_lesson_files(lesson_folder, lesson):
  if lesson.get('files'):
    for file in lesson['files']:
      lesson_file_folder = create_folder(shorten_folder_name(os.path.join(lesson_folder, 'material')))
      download_files(lesson_file_folder, file['name'], file['url'])


def process_lesson_content(lesson_folder, lesson):
  if lesson.get('content'):
    lesson_content_folder = create_folder(shorten_folder_name(os.path.join(lesson_folder, 'complemento')))
    save_html(lesson_content_folder, lesson['content'])


def get_lessons(module_folder, lessons):
  with ThreadPoolExecutor(max_workers=3) as executor:
    futures = []
    for i, lesson in enumerate(lessons, start=1):
      lesson_title = clear_folder_name(f'{i:03d} - {lesson["title"]}')
      lesson_folder = create_folder(shorten_folder_name(os.path.join(module_folder, lesson_title)))
      future_video = executor.submit(process_lesson_video,lesson_folder, lesson)
      future_files = executor.submit(process_lesson_files,lesson_folder, lesson)
      future_content = executor.submit(process_lesson_content,lesson_folder, lesson)
      futures.extend([future_video, future_files, future_content])
    for future in as_completed(futures):
      future.result()


def process_data_module(module_folder, data):
  for module_id, module_lesson in data.items():
    if len(module_lesson) > 0:
      module_folder = create_folder(shorten_folder_name(module_folder))
      get_lessons(module_folder, module_lesson)
    else:
      msg = f'Este módulo não possui conteudo: {module_folder}'
      logger(msg, warning=True)


def process_modules(data):
  for module_folder, module_info in data.items():
    module_folder = shorten_folder_name(module_folder)
    process_data_module(module_folder, module_info)


def get_modules(selected_folder, course_name, course_link):
  if selected_folder == '' or not os.path.exists(selected_folder):
    selected_folder = os.getcwd()
  response = kiwifysession.get(course_link).json()
  modules = response['course']['modules']
  course_folder = create_folder(os.path.join(selected_folder, clear_folder_name(course_name)))
  for i, module in enumerate(tqdm(modules, desc='Processing Modules', total=len(modules)), start=1):
    modules_data = {}
    module_id = module['id']
    module_name = os.path.join(course_folder, clear_folder_name(f'{i:03d} - {module["name"]}'))
    module_info = module['lessons']
    modules_data[module_name] = {module_id: module_info}
    process_modules(modules_data)


if __name__ == '__main__':
  course_name, course_link, selected_folder = selected_course
  modules_data = get_modules(selected_folder, course_name, course_link)
