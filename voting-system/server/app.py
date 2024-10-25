from flask import Flask, render_template, request
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os

print(os.getcwd())  # This will show the current working directory when the server runs
app = Flask(__name__, template_folder='../templates')

app.secret_key = 'your_secret_key'  # Change this for your app

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'  # Change to your MySQL password
app.config['MYSQL_DB'] = 'voting_system1'

mysql = MySQL(app)

# Home Route
@app.route('/')
def home():
    return render_template('login.html')
if __name__ == '__main__':
    app.run(debug=True)

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            session['has_voted'] = user[4]

            if user[3] == 'admin':
                return redirect(url_for('admin_panel'))
            elif user[3] == 'user' and not user[4]:
                return redirect(url_for('voting_page'))
            else:
                flash('You have already voted!')
                return redirect(url_for('home'))
        else:
            flash('Invalid credentials!')
            return redirect(url_for('home'))
    return render_template('login.html')

# Admin Panel
@app.route('/admin')
def admin_panel():
    if 'user_id' in session and session['role'] == 'admin':
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Participants")
        participants = cursor.fetchall()
        return render_template('admin_panel.html', participants=participants)
    return redirect(url_for('login'))

# Add Participants
@app.route('/add_participant', methods=['GET', 'POST'])
def add_participant():
    if 'user_id' in session and session['role'] == 'admin':
        if request.method == 'POST':
            name = request.form['name']
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO Participants (name) VALUES (%s)", (name,))
            mysql.connection.commit()
            flash('Participant added successfully!')
            return redirect(url_for('admin_panel'))
        return render_template('add_participant.html')
    return redirect(url_for('login'))

# Voting Page
@app.route('/vote', methods=['POST'])
def vote():
    if 'user_id' in session and session['role'] == 'user' and not session['has_voted']:
        participant_id = request.form['participant_id']
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE Participants SET vote_count = vote_count + 1 WHERE id = %s", (participant_id,))
        cursor.execute("UPDATE Users SET has_voted = 1 WHERE id = %s", (session['user_id'],))
        mysql.connection.commit()
        session['has_voted'] = True
        flash('Vote submitted successfully!')
        return redirect(url_for('home'))
    return redirect(url_for('home'))

# Remove Participant
@app.route('/remove_participant/<int:participant_id>')
def remove_participant(participant_id):
    if 'user_id' in session and session['role'] == 'admin':
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Participants WHERE id = %s", (participant_id,))
        mysql.connection.commit()
        flash('Participant removed successfully!')
        return redirect(url_for('admin_panel'))
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
