from flask import Flask, render_template, request, redirect, url_for
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

# Default data (can be removed if you want to start with an empty database)
default_data = {
    "John": date(2018, 12, 13),
    "Alice": date(2015, 2, 25),
    "sai": date(2001, 9, 2),
    "bunny": date(2005, 6, 10),
    "vasanth": date(1999, 9, 30),
}

# Function to insert default data into the database
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

    # Open the database connection
    conn = sqlite3.connect('birthday_data.db')
    cursor = conn.cursor()

    # Query the 'birthdays' table
    cursor.execute("SELECT name, birthdate FROM birthdays WHERE birthdate >= ? ORDER BY birthdate ASC LIMIT 1", (today,))
    row = cursor.fetchone()

    if row:
        nearest_name, nearest_birthday_str = row
        nearest_birthday = date.fromisoformat(nearest_birthday_str)  # Convert 'YYYY-MM-DD' string to date

    # Close the database connection
    conn.close()

    return nearest_name, nearest_birthday

@app.route('/viewdata')
def view_data():
    # Fetch all birthday data from the database
    conn = sqlite3.connect('birthday_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, birthdate FROM birthdays")
    data = cursor.fetchall()
    conn.close()
    print(data)
    return render_template('all_birthday.html', data=data)

@app.route('/')
def index():
    nearest_name, nearest_birthday = find_nearest_birthday()
    return render_template('index.html', nearest_name=nearest_name, nearest_birthday=nearest_birthday)

@app.route('/no_upcoming_birthday')
def no_upcoming_birthday():
    return render_template('upcoming_birthday.html')

# ... (other route handlers)
@app.route('/add_birthday', methods=['POST'])
def add_birthday():
    name = request.form['name']
    birthdate = request.form['birthdate']

    # Insert the new birthday into the database
    conn = sqlite3.connect('birthday_data.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO birthdays (name, birthdate) VALUES (?, ?)", (name, birthdate))
    conn.commit()
    conn.close()

    # Redirect to the page displaying all birthday data
    return redirect('/viewdata')
# Edit an existing birthday entry
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_birthday(id):
    # Fetch the existing data for editing
    conn = sqlite3.connect('birthday_data.db')
    cursor = conn.cursor()
    print(id)
    cursor.execute("SELECT name, birthdate FROM birthdays WHERE id=?", (id,))
    data = cursor.fetchone()
    conn.close()
    print(data)
    if data is None:
        # Handle the case where the ID does not exist
        # You can redirect to an error page or show an error message
        return "Birthday not found"

    if request.method == 'POST':
        name = request.form['name']
        birthdate = request.form['birthdate']

        # Update the entry in the database
        conn = sqlite3.connect('birthday_data.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE birthdays SET name=?, birthdate=? WHERE id=?", (name, birthdate, id))
        conn.commit()
        conn.close()

        # Redirect back to viewdata page after editing
        return redirect('/viewdata')

    # If data is not None, proceed with rendering the edit form
    return render_template('edit_birthday.html', id=id, name=data[0], birthdate=data[1])


@app.route('/delete/<int:id>')
def delete_birthday(id):
    # Delete the entry from the database
    conn = sqlite3.connect('birthday_data.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM birthdays WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/viewdata')


if __name__ == '__main__':
    app.run(debug=True)
