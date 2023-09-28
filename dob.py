from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from datetime import date
import sqlite3

app = Flask(__name__)

# Create a SQLite database and table
conn = sqlite3.connect('birthday_data.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS birthdays (
        id INTEGER PRIMARY KEY,
        name TEXT,
        birthdate DATE
    )
''')
conn.commit()
conn.close()

default_data = {
    "John": date(2018, 12, 13),
    "Alice": date(2015, 2, 25),
    "sai": date(2001, 9, 2),
    "bunny": date(2005, 6, 10),
    "vasanth": date(1999, 9, 30),
}

def insert_default_data():
    conn = sqlite3.connect('birthday_data.db')
    cursor = conn.cursor()
    for name, dob in default_data.items():
        dob_str = dob.strftime("%Y-%m-%d")  # Format date as 'YYYY-MM-DD'
        cursor.execute("INSERT INTO birthdays (name, birthdate) VALUES (?, ?)", (name, dob_str))
    conn.commit()
    conn.close()

def find_nearest_birthday():
    today = date.today()
    nearest_birthday = None
    nearest_name = None

    
    conn = sqlite3.connect('birthday_data.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name, birthdate FROM birthdays WHERE birthdate >= ? ORDER BY birthdate ASC LIMIT 1", (today,))
    row = cursor.fetchone()

    if row:
        nearest_name, nearest_birthday_str = row
        nearest_birthday = date.fromisoformat(nearest_birthday_str)  # Convert 'YYYY-MM-DD' string to date

    conn.close()

    return nearest_name, nearest_birthday

@app.route('/viewdata',methods=['GET'])
def view_data():
    conn = sqlite3.connect('birthday_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, birthdate FROM birthdays")
    data = cursor.fetchall()
    conn.close()
    # Check for a specific header that is commonly sent by Postman
    user_agent = request.headers.get('User-Agent')
    if 'Postman' in user_agent:
        return jsonify(data)
    else:
        # Request is from a web browser, return HTML response
        return render_template('all_birthday.html', data=data)

@app.route('/')
def index():
    nearest_name, nearest_birthday = find_nearest_birthday()
    return render_template('index.html', nearest_name=nearest_name, nearest_birthday=nearest_birthday)

#@app.route('/no_upcoming_birthday')
#def no_upcoming_birthday():
#
#    return render_template('upcoming_birthday.html')

@app.route('/add_birthday', methods=['POST'])
def add_birthday():
    if request.content_type == 'application/json':
        try:
            data = request.json  # Parse JSON data from the request
            name = data['name']
            birthdate = data['birthdate']

            conn = sqlite3.connect('birthday_data.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO birthdays (name, birthdate) VALUES (?, ?)", (name, birthdate))
            conn.commit()
            conn.close()

            response = make_response("Success", 200)
            return response
        except Exception as e:
            # Handle any errors that may occur, e.g., invalid JSON or missing keys
            return jsonify({'error': str(e)}), 400
    elif request.content_type == 'application/x-www-form-urlencoded':
        try:
            name = request.form['name']
            birthdate = request.form['birthdate']

            conn = sqlite3.connect('birthday_data.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO birthdays (name, birthdate) VALUES (?, ?)", (name, birthdate))
            conn.commit()
            conn.close()

            return redirect('/viewdata')
        except Exception as e:
            # Handle any errors that may occur with form data
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': 'Unsupported Content-Type'}), 400


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_birthday(id):
    conn = sqlite3.connect('birthday_data.db')
    cursor = conn.cursor()
    print(id)
    cursor.execute("SELECT name, birthdate FROM birthdays WHERE id=?", (id,))
    data = cursor.fetchone()
    conn.close()
    print(data)
    if data is None:
        return "Birthday not found"

    if request.method == 'POST':
        name = request.form['name']
        birthdate = request.form['birthdate']

        conn = sqlite3.connect('birthday_data.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE birthdays SET name=?, birthdate=? WHERE id=?", (name, birthdate, id))
        conn.commit()
        conn.close()

        return redirect('/viewdata')

    return render_template('edit_birthday.html', id=id, name=data[0], birthdate=data[1])

# Additional functionality to edit birthday using JSON
@app.route('/edit_json/<int:id>', methods=['POST'])
def edit_birthday_json(id):
    try:
        data = request.json  # Parse JSON data from the request
        name = data['name']
        birthdate = data['birthdate']

        conn = sqlite3.connect('birthday_data.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE birthdays SET name=?, birthdate=? WHERE id=?", (name, birthdate, id))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Birthday updated successfully'})
    except Exception as e:
        # Handle any errors that may occur when parsing JSON or updating data
        return jsonify({'error': str(e)}), 400

@app.route('/delete/<int:id>', methods=['POST'])
def delete_birthday(id):
    print("Hi")
    conn = sqlite3.connect('birthday_data.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM birthdays WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/viewdata')


if __name__ == '__main__':
    app.run(debug=True)


