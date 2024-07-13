import requests

from utils import alexandria_ascii_art, clear_screen


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


def get_courses(token):
  kiwifysession.headers['authorization'] = f'Bearer {token}'
  response = kiwifysession.get('https://admin-api.kiwify.com.br/v1/viewer/schools/courses?&archived=false', headers=headers).json()
  courses = response['courses']
  course_data = {}
  for course in courses:
    course_id = course['course_info']['id']
    course_name = course['course_info']['name']
    course_data[course_id] = course_name
  return course_data


def choose_course(courses):
  print('Cursos disponíveis:')
  for i, course_name in enumerate(courses.values(), start=1):
    print(f'{i}. {course_name}')
  choice = input("Escolha um curso pelo número: ")
  selected_course_id = list(courses.keys())[int(choice) - 1]
  selected_course_title = courses[selected_course_id]
  selected_course_link = f'https://admin-api.kiwify.com.br/v1/viewer/courses/{selected_course_id}'
  print(f'Link curso selecionado:', selected_course_title)
  print(f'O tamanho da pasta pode ocasionar erros devido a diretórios muito longos.')
  print(f'É opcional. Caso não coloque nada ou pasta inexistente, o download será feito na pasta desta tools.')
  selected_course_folder = input(f'Escolha a pasta para download: ').strip()
  return selected_course_title, selected_course_link, selected_course_folder

username, password = credentials()
token = get_token(username, password)
course_data = get_courses(token)
selected_course = choose_course(course_data)