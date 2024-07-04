from flask import Flask, request, jsonify, render_template
import requests
import sqlite3

app = Flask(__name__)

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
            'created_at': item['created_at']
        }
        vacancies.append(vacancy)
    return vacancies

def connect_db():
    conn = sqlite3.connect('hh_vacancies.db')
    return conn

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vacancies (
            id TEXT PRIMARY KEY,
            name TEXT,
            employer TEXT,
            description TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()

create_tables()

def clear_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM vacancies')
    conn.commit()


def load_to_db(vacancies):
    clear_table()
    conn = connect_db()
    cursor = conn.cursor()
    for vacancy in vacancies:
        cursor.execute('''
            INSERT OR REPLACE INTO vacancies (id, name, employer, description, created_at) 
            VALUES (?, ?, ?, ?, ?)
        ''', (vacancy['id'], vacancy['name'], vacancy['employer'], vacancy['description'], vacancy['created_at']))
    conn.commit()

def get_analytics():
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM vacancies')
    total_vacancies = cursor.fetchone()[0]
    
    cursor.execute('SELECT employer, COUNT(*) FROM vacancies GROUP BY employer ORDER BY COUNT(*) DESC LIMIT 5')
    top_employers = cursor.fetchall()

    conn.close()

    analytics_data = {
        'total_vacancies': total_vacancies,
        'top_employers': top_employers,
    }

    return analytics_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    text = request.args.get('text', 'Python разработчик')
    area = request.args.get('area', '1')
    page = request.args.get('page', '0')
    per_page = request.args.get('per_page', '10')
    
    params = {
        'text': text,
        'area': area,
        'page': int(page),
        'per_page': int(per_page)
    }
    
    vacancy_data = make_request(params)
    vacancies = get_vacancies(vacancy_data)
    load_to_db(vacancies)

    analytics = get_analytics()
    
    return jsonify({
        'vacancies': vacancies,
        'analytics': analytics
    })

if __name__ == '__main__':
    app.run(debug=True)