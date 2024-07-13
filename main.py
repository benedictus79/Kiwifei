from download import download_files, download_with_ytdlp
from login import selected_course, kiwifysession
from utils import clear_folder_name, os, create_folder, shorten_folder_name
from tqdm import tqdm


def check_url_player(lesson_name_media, url):
  if 'https://' not in url:
    url = f'https://d3pjuhbfoxhm7c.cloudfront.net{url}'
    download_with_ytdlp(lesson_name_media, url)
  elif 'vimeo' in url:
    download_with_ytdlp(lesson_name_media, url)


def get_lessons(module_folder, lessons):
  for i, lesson in enumerate(lessons, start=1):
    lesson_title = clear_folder_name(f'{i:03d} - {lesson["title"]}')
    lesson_folder = create_folder(shorten_folder_name(os.path.join(module_folder, lesson_title)))
    if lesson.get('files'):
      files = lesson['files']
      for file in files:
        lesson_file_folder = create_folder(os.path.join(module_folder, lesson_title, 'material'))
        download_files(lesson_file_folder, file['name'], file['url'])

    if lesson.get('video'):
      lesson_name_media = os.path.join(lesson_folder, 'aula')
      url = lesson['video']['stream_link']
      check_url_player(lesson_name_media, url)


def process_data_module(module_folder, data):
  for module_id, module_lesson in data.items():
    lessons = module_lesson
    get_lessons(module_folder, lessons)


def process_modules(data):
  for module_folder, module_info in data.items():
    module_folder = create_folder(shorten_folder_name(module_folder))
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