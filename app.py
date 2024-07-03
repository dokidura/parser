import requests

def make_request(params):
    url = 'https://api.hh.ru/vacancies'
    response = requests.get(url, params=params)
    data = response.json()
    return data

def get_vacancies(data):
    vacancies = []
    for item in data['items']:
        vacancy = {
            'id': item['id'],
            'name': item['name'],
            'employer': item['employer']['name'],
            'description': item['snippet']['responsibility'],
            'skills': ', '.join([skill['name'] for skill in item['key_skills']]) if 'key_skills' in item else '',
            'created_at': item['created_at']
        }
        vacancies.append(vacancy)
    return vacancies

params = {
    'text': 'Python'
}

print(make_request)