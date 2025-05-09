from flask import Flask, render_template, request, redirect, url_for, session, \
    flash, jsonify, send_file, send_from_directory
import random
import os
from datetime import datetime
import mentalhealth_chatbot
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

# Simple counter
visit_count = 100

ADMIN_PASSWORD = "admin123"  # You can change this anytime!

# Create users.txt and logs.txt if not present
if not os.path.exists('users.txt'):
    open('users.txt', 'w').close()
if not os.path.exists('logs.txt'):
    open('logs.txt', 'w').close()
if not os.path.exists('reviews.txt'):
    open('reviews.txt', 'w').close()


# IQ Questions Pool
questions_pool = [
    # Pattern Recognition
    {"question": "Which number logically follows this series: 2, 4, 8, 16, ?", "options": ["20", "24", "30", "32"], "answer": "32"},
    {"question": "Complete the sequence: 1, 1, 2, 3, 5, 8, ?", "options": ["11", "12", "13", "14"], "answer": "13"},
    {"question": "What comes next: 2, 6, 12, 20, ?", "options": ["28", "30", "32", "35"], "answer": "30"},
    {"question": "Find the next number: 3, 6, 12, 24, ?", "options": ["36", "42", "48", "54"], "answer": "48"},
    {"question": "Complete: 81, 27, 9, 3, ?", "options": ["0", "1", "2", "1.5"], "answer": "1"},
    
    # Letter Patterns
    {"question": "What letter comes next: A, C, E, G, ?", "options": ["H", "I", "J", "K"], "answer": "I"},
    {"question": "Complete the pattern: B, D, F, H, ?", "options": ["I", "J", "K", "L"], "answer": "J"},
    {"question": "Find the missing letter: M, J, G, D, ?", "options": ["A", "B", "C", "E"], "answer": "A"},
    {"question": "What comes next: Z, W, T, Q, ?", "options": ["O", "N", "P", "M"], "answer": "N"},
    {"question": "Complete: Y, U, Q, M, ?", "options": ["K", "I", "J", "L"], "answer": "I"},
    
    # Analogies
    {"question": "Foot is to Shoe as Hand is to?", "options": ["Glove", "Sandal", "Sock", "Hat"], "answer": "Glove"},
    {"question": "Book is to Reading as Fork is to?", "options": ["Drawing", "Writing", "Stirring", "Eating"], "answer": "Eating"},
    {"question": "Sky is to Blue as Grass is to?", "options": ["Long", "Green", "Growing", "Plant"], "answer": "Green"},
    {"question": "Bird is to Wing as Fish is to?", "options": ["Water", "Swim", "Fin", "Scale"], "answer": "Fin"},
    {"question": "Clock is to Time as Thermometer is to?", "options": ["Weather", "Heat", "Temperature", "Mercury"], "answer": "Temperature"},
    
    # Logical Reasoning
    {"question": "If all Bloops are Razzies and all Razzies are Lazzies, are all Bloops definitely Lazzies?", "options": ["Yes", "No", "Cannot be determined", "Maybe"], "answer": "Yes"},
    {"question": "If no cats like water, and Fluffy is a cat, does Fluffy like water?", "options": ["Yes", "No", "Maybe", "Not enough information"], "answer": "No"},
    {"question": "All mammals are warm-blooded. A dolphin is warm-blooded. Is a dolphin definitely a mammal?", "options": ["Yes", "No", "Cannot be determined", "Maybe"], "answer": "No"},
    {"question": "If red means stop and green means go, and yellow means neither stop nor go, what does blue mean?", "options": ["Stop", "Go", "Cannot be determined", "Neither"], "answer": "Cannot be determined"},
    {"question": "If A = B and B = C, is A always equal to C?", "options": ["Yes", "No", "Sometimes", "Cannot say"], "answer": "Yes"},
    
    # Odd One Out
    {"question": "Which one does NOT belong?", "options": ["Dog", "Mouse", "Lion", "Snake"], "answer": "Snake"},
    {"question": "Which word does NOT fit?", "options": ["Tulip", "Rose", "Bud", "Daisy"], "answer": "Bud"},
    {"question": "Find the odd one out:", "options": ["Apple", "Banana", "Carrot", "Orange"], "answer": "Carrot"},
    {"question": "Which doesn't belong?", "options": ["Piano", "Violin", "Guitar", "Flute"], "answer": "Piano"},
    {"question": "Odd one out:", "options": ["Mercury", "Venus", "Sun", "Mars"], "answer": "Sun"},
    
    # Word Relations
    {"question": "Which word is a synonym of 'trust'?", "options": ["Doubt", "Reliance", "Fear", "Ignorance"], "answer": "Reliance"},
    {"question": "Which is the opposite of 'brave'?", "options": ["Strong", "Weak", "Cowardly", "Fearless"], "answer": "Cowardly"},
    {"question": "Happy is to Sad as Rich is to?", "options": ["Money", "Poor", "Wealth", "Fortune"], "answer": "Poor"},
    {"question": "Choose the word most similar to 'Enormous':", "options": ["Tiny", "Giant", "Average", "Normal"], "answer": "Giant"},
    {"question": "Find the antonym of 'Ancient':", "options": ["Old", "Modern", "Aged", "Traditional"], "answer": "Modern"}
]

# ------------------------- Logging Function -------------------------
def save_log(message, username=None, session_start=False, session_end=False):
    with open('logs.txt', 'a', encoding='utf-8') as f:
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

        if session_start and username:
            f.write(f"\n==== SESSION START: {username} ====\n")
        elif session_end and username:
            f.write(f"==== SESSION END: {username} ====\n")
        else:
            f.write(f"{timestamp} {message}\n")


# ------------------------- LOGIN/SIGNUP/LOGOUT Routes -------------------------

def save_user(username):
    with open('users.txt', 'a') as f:
        f.write(username + '\n')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global visit_count
    if request.method == 'POST':
        username = request.form['username'].strip()

        with open('users.txt', 'r') as f:
            users = [line.strip() for line in f.readlines()]

        if username in users:
            session['username'] = username
            flash(f"Welcome {username}! 🎉", 'success')
            save_log(f"User logged in: {username}", username=username, session_start=True)
            return redirect(url_for('home'))
        else:
            flash('User not found. Please sign up first.', 'error')
            save_log(f"Failed login attempt: {username}")
            return redirect(url_for('signup'))

    return render_template('login.html', visit_count=visit_count)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    global visit_count
    if request.method == 'POST':
        username = request.form['username'].strip()

        with open('users.txt', 'r') as f:
            users = [line.strip() for line in f.readlines()]

        if username in users:
            flash('Username already exists. Please try a different one.', 'warning')
            return redirect(url_for('signup'))
        else:
            save_user(username)
            session['username'] = username
            flash('Account created successfully! 🎉', 'success')
            save_log(f"New account created: {username}")
            return redirect(url_for('home'))

    return render_template('signup.html', visit_count=visit_count)

@app.route('/logout')
def logout():
    username = session.pop('username', None)
    flash('Logged out successfully 👋', 'info')
    if username:
        save_log(f"User logged out: {username}", username=username, session_end=True)
    return redirect(url_for('login'))

# Admin Login Page
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            session['admin'] = True
            flash('Admin login successful! 🔥', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Wrong Admin Password! ❌', 'error')
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html', visit_count=visit_count)

# Admin Logs Panel
@app.route('/admin')
def admin_panel():
    if not session.get('admin'):
        flash('Unauthorized access! 🚫', 'error')
        return redirect(url_for('admin_login'))

    logs_content = ""
    try:
        with open('logs.txt', 'r') as f:
            logs_content = f.read()
    except FileNotFoundError:
        logs_content = "No logs found."

    return render_template('admin.html', logs=logs_content, visit_count=visit_count)

# Admin Logout
@app.route('/admin_logout')
def admin_logout():
    session.pop('admin', None)
    flash('Admin logged out successfully 👋', 'info')
    return redirect(url_for('login'))

@app.route('/download_logs')
def download_logs():
    if not session.get('admin'):
        flash('Unauthorized access! 🚫', 'error')
        return redirect(url_for('admin_login'))

    return send_file('logs.txt', as_attachment=True)

# Add this near your other routes
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                             'favicon.ico', mimetype='image/vnd.microsoft.icon')

# ------------------------- MAIN ROUTES -------------------------

@app.route('/')
def home():
    global visit_count
    if 'username' not in session:
        return redirect(url_for('login'))
    visit_count += 1
    save_log(f"Visited Home Page - User: {session['username']}")
    return render_template('home.html', visit_count=visit_count)

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'GET':
        # Load conversation history for this user
        history = mentalhealth_chatbot.get_chat_history(session['username'])
        return render_template('chatbot.html', chat_history=history)
    
    elif request.method == 'POST':
        if request.is_json:
            # API-style request
            data = request.get_json()
            message = data.get('message', '')
            action = data.get('action', 'chat')
        else:
            # Form-style request
            message = request.form.get('message', '')
            action = request.form.get('action', 'chat')
        
        # Handle empty message
        if not message and action == 'chat':
            return jsonify({
                "success": False,
                "message": "Please enter a message"
            })
        
        user_id = session.get('username', 'anonymous')
        
        if action == 'chat':
            # Process regular chat message
            response = mentalhealth_chatbot.generate_response(message, user_id)
            
            # Log the interaction
            save_log(f"Chatbot interaction - User: {user_id} - Message: '{message}'")
            
            return jsonify({
                "success": True,
                "message": response,
                "chatHistory": mentalhealth_chatbot.get_chat_history(user_id)
            })
            
        elif action == 'affirmation':
            # Generate an affirmation
            affirmation = mentalhealth_chatbot.generate_affirmation()
            save_log(f"User {user_id} requested an affirmation")
            return jsonify({
                "success": True,
                "affirmation": affirmation
            })
            
        elif action == 'meditation':
            # Generate a meditation guide
            meditation = mentalhealth_chatbot.generate_meditation_guide()
            save_log(f"User {user_id} requested a meditation guide")
            return jsonify({
                "success": True,
                "meditation": meditation
            })
    
        return jsonify({"success": False, "message": "Invalid action"})

# Route to clear chat history
@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    if 'username' not in session:
        return jsonify({"status": "error", "message": "Not logged in"})
    
    mentalhealth_chatbot.clear_chat_history(session['username'])
    save_log(f"User {session['username']} cleared their chat history")
    
    return jsonify({"status": "success", "message": "Chat history cleared"})

# Gets background image as base64 (helper function)
@app.route('/background_image')
def get_background_image():
    try:
        with open('static/images/background.png', 'rb') as f:
            image_data = f.read()
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        return jsonify({
            "success": True,
            "image": encoded_image
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/iq_test', methods=['GET', 'POST'])
def iq_test():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_answers = request.form
        score = 0
        # Get the questions from session to match with user's answers
        test_questions = session.get('test_questions', [])
        for i, q in enumerate(test_questions):
            if user_answers.get(f"q{i}") == q['answer']:
                score += 10
        save_log(f"User {session['username']} completed IQ Test with Score: {score}")
        return render_template('iq_result.html', score=score, visit_count=visit_count)
    
    # Randomly select 10 questions for this attempt
    session['test_questions'] = random.sample(questions_pool, 10)
    save_log(f"User {session['username']} started IQ Test")
    return render_template('iq_test.html', questions=session['test_questions'], visit_count=visit_count)

@app.route('/mindfulness')
def mindfulness():
    if 'username' not in session:
        return redirect(url_for('login'))

    save_log(f"User {session['username']} visited Mindfulness Music")
    songs = ['music/song1.mp3', 'music/song2.mp3']
    return render_template('mindfulness.html', songs=songs, visit_count=visit_count)

@app.route('/about')
def about():
    if 'username' not in session:
        return redirect(url_for('login'))

    save_log(f"User {session['username']} visited About Page")
    return render_template('about.html', visit_count=visit_count)

@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    global visit_count
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        review = request.form['review']
        rating = request.form['rating']
        with open('reviews.txt', 'a', encoding='utf-8') as f:
            f.write(f"{review}||{rating}\n")
        save_log(f"User {session['username']} submitted a Review: {rating}⭐ - {review}")
        return redirect(url_for('reviews'))

    all_reviews = []
    try:
        with open('reviews.txt', 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('||')
                if len(parts) == 2:
                    all_reviews.append(parts)
    except FileNotFoundError:
        pass

    save_log(f"User {session['username']} visited Reviews Page")
    return render_template('reviews.html', reviews=all_reviews, visit_count=visit_count)

# -------------------------
if __name__ == '__main__':
    app.run(debug=True)