from flask import Flask, render_template, request, redirect, url_for



app = Flask(__name__)

# Данные пользователя (временное хранилище)
user_data = {
    'id': 1,
    'first_name': 'Иван',
    'last_name': 'Иванов',
    'email': 'ivanov@example.com',
    'password': 'secret123'
}

# Записи пользователя (временное хранилище)
user_entries = [
    {'id': 1, 'title': 'Тест1', 'content': 'Текстовый тест'},
    {'id': 2, 'title': 'Тест2', 'content': 'Текстовый текст'},
    {'id': 3, 'title': 'Тест3', 'content': 'Тестовый тест'}
]


@app.route('/')
def index():
    return render_template('index.html', user=user_data, entries=user_entries)


@app.route('/update-user', methods=['POST'])
def update_user():
    user_data['first_name'] = request.form['first_name']
    user_data['last_name'] = request.form['last_name']
    user_data['email'] = request.form['email']

    if request.form['password']:
        user_data['password'] = request.form['password']

    return redirect(url_for('index'))


@app.route('/add-entry', methods=['POST'])
def add_entry():
    new_id = max([e['id'] for e in user_entries], default=0) + 1
    user_entries.append({
        'id': new_id,
        'title': request.form['title'],
        'content': request.form['content']
    })
    return redirect(url_for('index'))


@app.route('/update-entry/<int:entry_id>', methods=['POST'])
def update_entry(entry_id):
    for entry in user_entries:
        if entry['id'] == entry_id:
            entry['title'] = request.form['title']
            entry['content'] = request.form['content']
            break
    return redirect(url_for('index'))


@app.route('/delete-entry/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    global user_entries
    user_entries = [e for e in user_entries if e['id'] != entry_id]
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)