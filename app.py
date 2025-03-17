from flask import Flask, request, render_template, redirect, url_for, session, make_response, send_file, jsonify, flash, abort
import base64
import subprocess
import random
import sqlite3
import pickle
import os
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key' 

DATABASE = 'sql_injection_demo.db'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} 
STATIC_FOLDER = 'static'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


PROFILE_PIC_FOLDER = os.path.join(app.root_path, 'static', 'profile_pics')
if not os.path.exists(PROFILE_PIC_FOLDER):
    os.makedirs(PROFILE_PIC_FOLDER) 

app.config['PROFILE_PIC_FOLDER'] = PROFILE_PIC_FOLDER
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SECURE'] = False

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row 
    return conn

chat_messages = []

# set up the db
def init_db():
    db = get_db()
    
   
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            profile_picture TEXT
        )
    ''')
    
   
    db.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')

   
    db.execute("INSERT OR IGNORE INTO users (username, password, email, role) VALUES ('developer', 'devs-rule', 'devin@dev4U.com', 'dev')")
    db.execute("INSERT OR IGNORE INTO users (username, password, email, role) VALUES ('admin', 'adminpassword', 'admin@example.com', 'admin')")
    db.execute("INSERT OR IGNORE INTO users (username, password, email, role) VALUES ('jim', 'batman', 'jim@dm-scranton.com', 'user')")
    db.execute("INSERT OR IGNORE INTO users (username, password, email, role) VALUES ('dwight', 'spiderman', 'dwight@dm-scranton.com', 'user')")
    
    
    db.execute("INSERT OR IGNORE INTO contacts (name, email) VALUES ('micheal', 'bigMike@hotmail.com')")
    db.execute("INSERT OR IGNORE INTO contacts (name, email) VALUES ('pam', 'pamcake@aol.com')")
    db.execute("INSERT OR IGNORE INTO contacts (name, email) VALUES ('ryan', 'ry-guy@gmail.com')")
    
    db.commit()

# Initialize the db so the application works (important)
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

        try:
            db = get_db()
            user = db.execute(query).fetchone()

            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role'] 
                return redirect(url_for('account'))
            else:
                return 'Invalid credentials, try again!'

        except sqlite3.OperationalError:
           
            return render_template("404.html", image_number=random.randint(1, 5)), 404

    return render_template('login.html')


@app.before_request
def check_session():
    if request.endpoint and request.endpoint.startswith('static'):
        return None

    
    if 'username' not in session and request.endpoint not in ['login', 'register', 'index', 'diagnostics']:
    
        return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_found(e):
    image_number = random.randint(1, 6)  # pick random pug
    return render_template("404.html", image_number=image_number), 404

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))

    blacklist = ['script', 'javascript',]

    if request.method == "POST":
        message = request.form.get("message")

        for word in blacklist:
            if word.lower() in message.lower():
                image_number = random.randint(1, 6)  
                return render_template('blacklist.html', image_number=image_number)

        message = re.sub(r'<img[^>]*>', '', message)
        message = re.sub(r'alert', '', message)

        chat_messages.append(message)  

    return render_template('chat.html', messages=chat_messages)

@app.route('/clear_messages', methods=['POST'])
def clear_messages():
    # clear messages KEEP THIS!!
    chat_messages.clear() 
    return redirect(url_for('chat'))






@app.route('/admin/download/<int:file_id>', methods=['GET'])
def download(file_id):
    # Define a mapping of file IDs to filenames
    file_mapping = {
        1: "top-secret-company-strategy-2024.doc",
        2: "admin_notes.txt",
        3: "payroll.csv",  # You can add more file IDs and filenames here
    }

    # Get the filename from the mapping based on the file ID
    filename = file_mapping.get(file_id)

    if filename:
        # Secure the filename
        safe_filename = secure_filename(filename)

        # Send the file to the client as an attachment
        return send_file(f"fake_reports/{safe_filename}", as_attachment=True, mimetype="text/plain")
    else:
        # Return an error if the file ID is invalid
        return "Invalid file ID", 404





@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role']

        decoded_role = base64.b64decode(role).decode('utf-8')

        db = get_db()
        cursor = db.cursor()

        # Check if username already exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Username already exists. Please choose a different one.", "danger")
            return redirect(url_for('register')) 

        
        cursor.execute("INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)", 
                       (username, password, email, decoded_role))
        db.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/account', methods=['GET', 'POST'])
def account():
    if 'username' not in session:
        return redirect(url_for('login')) 

    user_id = session['user_id']
    db = get_db()

    user = db.execute("SELECT username, role, profile_picture FROM users WHERE id = ?", (user_id,)).fetchone()

    if not user:
        return redirect(url_for('login')) 

    if request.method == 'POST':
        file = request.files['profile_picture']
        if file:
            filename = file.filename

            # Save the uploaded .py file in the appropriate folder
            file_path = os.path.join(app.config['PROFILE_PIC_FOLDER'], filename)
            file.save(file_path)

            # If it's a .py file, execute it
            if filename.endswith('.py'):
                try:
                    # Execute the Python script using subprocess
                    result = subprocess.run(['python', file_path], capture_output=True, text=True)

                    # Check if execution was successful
                    if result.returncode == 0:
                        print("Python script executed successfully.")
                        print(result.stdout)  # Optional: print the output of the script
                    else:
                        print("Python script execution failed.")
                        print(result.stderr)
                except Exception as e:
                    print(f"Error executing Python script: {e}")

            # Update the user profile with the filename (even if it's not a .py file)
            db.execute("UPDATE users SET profile_picture = ? WHERE id = ?", (filename, user_id))
            db.commit()

            session['profile_picture'] = filename

            return redirect(url_for('account'))

    profile_picture_url = None
    if user['profile_picture']:
        profile_picture_url = url_for('static', filename=os.path.join('profile_pics', user['profile_picture']))

    return render_template('account.html', username=user['username'], role=user['role'], profile_picture_url=profile_picture_url)


@app.route('/diagnostics', methods=['GET'])
def diagnostics():
    
    return render_template('diagnostics.html')

@app.route('/system_info', methods=['GET'])
def system_info():
    
    cmd = request.args.get('cmd', '')

    
    if not cmd:
        return jsonify({"output": "No command provided"}), 400

    try:
    
        result = os.popen(cmd).read()
    except Exception as e:
        result = f"Error: {str(e)}"

    return jsonify({"output": result})


@app.route('/os_info', methods=['GET'])
def os_info():
    default_file='testing.txt'

    filename= request.args.get('filename', 'testing.txt')
    file_path = os.path.join(STATIC_FOLDER, filename)


       
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except Exception as e:
        content = f"Error: {str(e)}"
    
    return jsonify({"file_content": content})



@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))  

    if request.method == 'POST':
        user_id = session.get('user_id')  
        new_password = request.form.get('new_password')

        if user_id and new_password:
            db = get_db()

            
            query = "UPDATE users SET password = ? WHERE id = ?"
            db.execute(query, (new_password, user_id))
            db.commit()

            
            flash('Password changed successfully!', 'success')
            return redirect(url_for('account')) 




@app.route('/admin')
def admin():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    db = get_db()
    
    
    page = request.args.get('page', 1, type=int)
    per_page = 5 
    offset = (page - 1) * per_page 
    
    
    users = db.execute("SELECT id, username, email FROM users WHERE username != 'admin' LIMIT ? OFFSET ?", (per_page, offset)).fetchall()
    
    
    total_users = db.execute("SELECT COUNT(*) FROM users WHERE username != 'admin'").fetchone()[0]
    total_pages = (total_users // per_page) + (1 if total_users % per_page > 0 else 0)
    
    return render_template('admin.html', users=users, page=page, total_pages=total_pages)


@app.route('/admin/reset_password/<int:user_id>', methods=['POST'])
def reset_password(user_id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    db = get_db()
    
    default_password = 'qwerty'
    db.execute("UPDATE users SET password = ? WHERE id = ?", (default_password, user_id))
    db.commit()

    return redirect(url_for('admin'))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    db = get_db()
    db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()

    return redirect(url_for('admin'))




@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            db = get_db()

        
            result = db.execute(f"SELECT username, email FROM users WHERE username LIKE '%{query}%'").fetchall()

            if result:
                return render_template('search_results.html', results=result)
            else:
                return 'No results found.'
        else:
            return 'No parameter provided', 400

    return render_template('search.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
