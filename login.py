import requests
from utils import os, re, alexandria_ascii_art, clear_screen


kiwifysession = requests.Session()

headers = {
  'accept': 'application/json, text/plain, */*',
  'accept-language': 'pt-BR,pt;q=0.9',
  'cache-control': 'no-cache',
  'content-type': 'application/json;charset=UTF-8',
  'origin': 'https://dashboard.kiwify.com.br',
  'pragma': 'no-cache',
  'priority': 'u=1, i',
  'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Brave";v="126"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-site',
  'sec-gpc': '1',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
}

def credentials():
  alexandria_ascii_art()
  username = input('email: ')
  password = input('senha: ')
  clear_screen()
  return username, password


def get_token(username, password):
  json_data = {
    'email': username,
    'password': password,
    'returnSecureToken': True,
  }

  response = kiwifysession.post('https://admin-api.kiwify.com.br/v1/handleAuth/login', headers=headers, json=json_data).json()
  return response['idToken']


def extract_course_info(course, pattern):
  for key, value in course.items():
    if pattern.match(key):
      return key, value['id'], value['name']
  return None, None, None


def extract_school_id(school):
  school_id = kiwifysession.get(f'https://admin-api.kiwify.com.br/v1/viewer/schools/{school}/courses').json()['my_courses'][0]['id']
  return school_id


def get_courses(token):
  kiwifysession.headers['authorization'] = f'Bearer {token}'
  response = kiwifysession.get('https://admin-api.kiwify.com.br/v1/viewer/schools/courses?&archived=false', headers=headers).json()
  courses = response['courses']
  course_data = {}
  pattern = re.compile(r'^(course_info|school_info)$')

  for course in courses:
    info_type, course_id, course_name = extract_course_info(course, pattern)
    if course_id and course_name:
      if info_type == 'school_info':
        school_id = extract_school_id(course_id)
        course_data[school_id] = course_name
      else:
        course_data[course_id] = course_name

  return course_data


def choose_course(courses):
  print('Courses:')
  for i, course_name in enumerate(courses.values(), start=1):
    print(f'{i}. {course_name}')
  choice = input("Choose a course by number: ")
  selected_course_id = list(courses.keys())[int(choice) - 1]
  selected_course_title = courses[selected_course_id]
  selected_course_link = f'https://admin-api.kiwify.com.br/v1/viewer/courses/{selected_course_id}'
  print(f'Selected course link:', f'https://dashboard.kiwify.com.br/course/{selected_course_id}')
  print(f'The folder size may cause errors due to excessively long directories.')
  print(f'If you do not specify anything or if the folder does not exist, the download will be done in the folder: {os.getcwd()}.')
  selected_course_folder = input(f'Choose the folder for download: ').strip()
  return selected_course_title, selected_course_link, selected_course_folder

username, password = credentials()
token = get_token(username, password)
course_data = get_courses(token)
selected_course = choose_course(course_data)