import requests
import sqlite3
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

with sqlite3.connect('database.db') as db:
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vacancies (
            id TEXT PRIMARY KEY,
            name TEXT,
            employer TEXT,
            description TEXT,
            skills TEXT,
            created_at TEXT
        )
    ''')
    db.commit()

def load_to_db(vacancies):
    for vacancy in vacancies:
        cursor.execute('''
            INSERT OR REPLACE INTO vacancies (id, name, employer, description, skills, created_at) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (vacancy['id'], vacancy['name'], vacancy['employer'], vacancy['description'], vacancy['skills'], vacancy['created_at']))
    db.commit()
