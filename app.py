from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import matplotlib.pyplot as plt
import io
import base64
from PIL import Image
import random
import hashlib
from init_db import init_db
from dotenv import load_dotenv
import os
import secrets

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Set the secret key from environment variable or generate a random one if not set
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(16))

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def set_user_seed(email):
    seed = int(hashlib.sha256(email.encode()).hexdigest(), 16) % (2**32)
    random.seed(seed)

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user'] = email
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            flash('Passwords do not match')
        else:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
                conn.commit()
                conn.close()
                flash('Account created successfully! You can now log in.')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Email already registered')
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/science-careers')
def science_careers():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('science_careers.html')

@app.route('/commerce-careers')
def commerce_careers():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('commerce_careers.html')

@app.route('/arts-careers')
def arts_careers():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('arts_careers.html')

app.route('/counseling')
def counseling():
    return render_template('counseling.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/aptitude-test', methods=['GET', 'POST'])
def aptitude_test():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        standard = request.form.get('standard')
        if standard not in ['8', '9', '10']:
            flash('Please select a valid standard (8, 9, or 10)')
            return render_template('aptitude_test.html', standards=[8, 9, 10])
        return redirect(url_for('take_test', standard=standard))
    return render_template('aptitude_test.html', standards=[8, 9, 10])

# Question pools
science_questions_8 = [
    {"id": 1, "question": "Which of the following is a scalar quantity?", "options": ["Velocity", "Displacement", "Speed", "Force"], "correct": "Speed"},
    {"id": 2, "question": "What is the SI unit of distance?", "options": ["Meter", "Kilometer", "Second", "Newton"], "correct": "Meter"},
    {"id": 3, "question": "Which of the following is NOT a type of motion?", "options": ["Linear", "Circular", "Rotational", "Constant"], "correct": "Constant"},
    {"id": 4, "question": "A car travels 100 km in 2 hours. What is its average speed?", "options": ["25 km/h", "50 km/h", "100 km/h", "200 km/h"], "correct": "50 km/h"},
    {"id": 5, "question": "If an object is moving at a constant speed in a circular path, it is experiencing:", "options": ["Translational motion", "Uniform motion", "Uniform circular motion", "Irregular motion"], "correct": "Uniform circular motion"},
    {"id": 6, "question": "Which term describes a change in position with respect to time?", "options": ["Acceleration", "Speed", "Motion", "Inertia"], "correct": "Motion"}
]

science_questions_9 = [
    {"id": 1, "question": "What happens to the velocity of an object if it moves with uniform motion?", "options": ["Increases", "Decreases", "Remains constant", "Changes randomly"], "correct": "Remains constant"},
    {"id": 2, "question": "A bus moving in a straight line at constant speed is an example of:", "options": ["Uniform motion", "Non-uniform motion", "Random motion", "Circular motion"], "correct": "Uniform motion"},
    {"id": 3, "question": "What is the displacement of an object if it returns to its starting point?", "options": ["Equal to total distance", "Half of total distance", "Zero", "Infinite"], "correct": "Zero"},
    {"id": 4, "question": "Which of the following has both magnitude and direction?", "options": ["Speed", "Velocity", "Distance", "Time"], "correct": "Velocity"},
    {"id": 5, "question": "The rate of change of velocity is called:", "options": ["Speed", "Acceleration", "Displacement", "Time"], "correct": "Acceleration"},
    {"id": 6, "question": "A car moves at 20 m/s and then accelerates to 40 m/s in 10 seconds. What is its acceleration?", "options": ["2 m/s²", "4 m/s²", "10 m/s²", "20 m/s²"], "correct": "2 m/s²"}
]

science_questions_10 = [
    {"id": 1, "question": "An object moving with constant velocity has an acceleration of:", "options": ["Zero", "1 m/s²", "10 m/s²", "Infinity"], "correct": "Zero"},
    {"id": 2, "question": "The area under a speed-time graph represents:", "options": ["Velocity", "Acceleration", "Distance traveled", "Force"], "correct": "Distance traveled"},
    {"id": 3, "question": "A car moving with decreasing speed experiences:", "options": ["Positive acceleration", "Negative acceleration", "Zero acceleration", "Constant speed"], "correct": "Negative acceleration"},
    {"id": 4, "question": "If velocity changes, which of the following must occur?", "options": ["A force is applied", "Mass changes", "Gravity disappears", "Object moves in a straight line"], "correct": "A force is applied"},
    {"id": 5, "question": "An object moves in a straight line with uniform acceleration. What is its motion called?", "options": ["Circular motion", "Uniform linear motion", "Uniformly accelerated motion", "Random motion"], "correct": "Uniformly accelerated motion"},
    {"id": 6, "question": "Which of the following is NOT an example of acceleration?", "options": ["A speeding car", "A falling apple", "A parked bicycle", "A turning bus"], "correct": "A parked bicycle"}
]

maths_questions_8 = [
    {"id": 1, "question": "What is 1/2 of 100?", "options": ["25", "50", "75", "100"], "correct": "50"},
    {"id": 2, "question": "Convert 0.75 into a fraction.", "options": ["3/4", "1/2", "2/3", "1/4"], "correct": "3/4"},
    {"id": 3, "question": "What is 25% of 200?", "options": ["25", "50", "75", "100"], "correct": "50"},
    {"id": 4, "question": "If 3/5 of a number is 60, what is the number?", "options": ["80", "90", "100", "110"], "correct": "100"},
    {"id": 5, "question": "What is 0.4 × 0.2?", "options": ["0.08", "8", "0.8", "0.10"], "correct": "0.08"},
    {"id": 6, "question": "Convert 3/8 into a decimal.", "options": ["0.25", "0.375", "0.50", "0.625"], "correct": "0.375"}
]

maths_questions_9 = [
    {"id": 1, "question": "What is 10% of 450?", "options": ["45", "50", "40", "55"], "correct": "45"},
    {"id": 2, "question": "Find the missing value: 2/7 = ?/35", "options": ["5", "7", "9", "10"], "correct": "10"},
    {"id": 3, "question": "What is the decimal equivalent of 5/8?", "options": ["0.50", "0.625", "0.75", "0.80"], "correct": "0.625"},
    {"id": 4, "question": "Which fraction is the largest?", "options": ["2/5", "3/7", "4/9", "5/11"], "correct": "4/9"},
    {"id": 5, "question": "A book costs ₹120. If you buy 4 books, how much will it cost?", "options": ["480", "500", "460", "490"], "correct": "480"},
    {"id": 6, "question": "If a train travels 60 km in 1 hour, how far will it go in 3 hours?", "options": ["150 km", "160 km", "180 km", "200 km"], "correct": "180 km"}
]

maths_questions_10 = [
    {"id": 1, "question": "What is the square root of 144?", "options": ["12", "10", "14", "16"], "correct": "12"},
    {"id": 2, "question": "What is 5²?", "options": ["25", "20", "30", "15"], "correct": "25"},
    {"id": 3, "question": "What is 15% of 200?", "options": ["30", "25", "35", "40"], "correct": "30"},
    {"id": 4, "question": "What is 120 ÷ 8?", "options": ["15", "16", "14", "12"], "correct": "15"},
    {"id": 5, "question": "What is the value of 2³?", "options": ["8", "6", "10", "12"], "correct": "8"},
    {"id": 6, "question": "Find the missing term: B, D, G, K, ?", "options": ["P", "O", "N", "M"], "correct": "P"}
]

reasoning_questions_8 = [
    {"id": 1, "question": "Find the missing term: 1, 4, 9, 16, 25, ?", "options": ["36", "49", "42", "48"], "correct": "36"},
    {"id": 2, "question": "What comes next? 1, 2, 4, 8, 16, ?", "options": ["32", "30", "36", "40"], "correct": "32"},
    {"id": 3, "question": "Find the missing term: 0, 1, 1, 2, 3, 5, 8, ?", "options": ["13", "11", "14", "15"], "correct": "13"},
    {"id": 4, "question": "Find the missing term: 3C, 6F, 9I, 12L, ?", "options": ["15O", "15F", "16N", "17M"], "correct": "15O"},
    {"id": 5, "question": "What comes next? A, C, F, J, ?", "options": ["O", "N", "M", "P"], "correct": "O"},
    {"id": 6, "question": "Which number should replace the question mark? 121, 144, 169, ?, 225", "options": ["196", "199", "202", "216"], "correct": "196"}
]

# Placeholder for missing reasoning questions (assuming similar structure)
reasoning_questions_9 = reasoning_questions_8  # Replace with actual questions if available
reasoning_questions_10 = reasoning_questions_8  # Replace with actual questions if available

@app.route('/take-test/<int:standard>', methods=['GET', 'POST'])
def take_test(standard):
    if 'user' not in session:
        return redirect(url_for('login'))

    if standard == 8:
        science_pool = science_questions_8
        maths_pool = maths_questions_8
        reasoning_pool = reasoning_questions_8
    elif standard == 9:
        science_pool = science_questions_9
        maths_pool = maths_questions_9
        reasoning_pool = reasoning_questions_9
    else:
        science_pool = science_questions_10
        maths_pool = maths_questions_10
        reasoning_pool = reasoning_questions_10

    set_user_seed(session['user'])
    science_questions = random.sample(science_pool, 5)
    maths_questions = random.sample(maths_pool, 5)
    reasoning_questions = random.sample(reasoning_pool, 5)

    if request.method == 'POST':
        science_score = 0
        maths_score = 0
        reasoning_score = 0

        # Calculate science score
        for question in science_questions:
            answer = request.form.get(f"science[{question['id']}]")
            if answer == question['correct']:
                science_score += 1

        # Calculate maths score
        for question in maths_questions:
            answer = request.form.get(f"maths[{question['id']}]")
            if answer == question['correct']:
                maths_score += 1

        # Calculate reasoning score
        for question in reasoning_questions:
            answer = request.form.get(f"reasoning[{question['id']}]")
            if answer == question['correct']:
                reasoning_score += 1

        total_score = science_score + maths_score + reasoning_score

        # Counseling logic
        if science_score >= 4 and total_score >= 10:
            counseling_stream = 'Science'
            counseling_reason = 'Your strong science score suggests aptitude for scientific fields.'
        elif maths_score >= 4 and total_score >= 9:
            counseling_stream = 'Commerce'
            counseling_reason = 'Your math skills indicate potential for commerce fields.'
        else:
            counseling_stream = 'Arts'
            counseling_reason = 'Your balanced skills suggest exploring creative fields.'

        # Save results
        conn = get_db_connection()
        try:
            conn.execute("""
                INSERT INTO test_results 
                (user_email, standard, science_score, maths_score, reasoning_score, total_score, counseling_stream, counseling_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (session['user'], standard, science_score, maths_score, reasoning_score, total_score, counseling_stream, counseling_reason))
            conn.commit()
        except sqlite3.Error as e:
            app.logger.error(f"Database error: {e}")
            flash('Error saving test results')
        finally:
            conn.close()

        return redirect(url_for('test_results'))

    return render_template('take_test.html', standard=standard, science_questions=science_questions, maths_questions=maths_questions, reasoning_questions=reasoning_questions)

@app.route('/test-results')
def test_results():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM test_results WHERE user_email = ? ORDER BY test_date DESC', (session['user'],))
    results = cursor.fetchall()
    conn.close()
    if not results:
        return render_template('test_results.html', results=None)
    
    latest_result = results[0]
    science_score = latest_result['science_score']
    maths_score = latest_result['maths_score']
    reasoning_score = latest_result['reasoning_score']

    # Create performance graph
    plt.figure(figsize=(8, 6))
    categories = ['Science', 'Maths', 'Reasoning']
    scores = [science_score, maths_score, reasoning_score]
    plt.plot(categories, scores, marker='o', linestyle='-', color='#ec4899', linewidth=2, markersize=10)
    plt.fill_between(categories, scores, color='#ec4899', alpha=0.2)
    plt.title('Aptitude Test Performance', fontsize=16, color='#4b5563')
    plt.ylabel('Score (out of 5)', fontsize=12, color='#4b5563')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.ylim(0, 5)

    # Convert plot to image
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    graph = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()

    # Generate recommendations
    recommendations = []
    if science_score < 3:
        recommendations.append("Focus on improving your scientific concepts through practice.")
    if maths_score < 3:
        recommendations.append("Work on mathematical problem-solving techniques.")
    if reasoning_score < 3:
        recommendations.append("Practice logical reasoning exercises to improve.")

    # Determine counseling stream color
    stream = latest_result['counseling_stream']
    if stream == 'Science':
        stream_color = 'bg-green-100 text-green-800'
    elif stream == 'Commerce':
        stream_color = 'bg-blue-100 text-blue-800'
    else:
        stream_color = 'bg-purple-100 text-purple-800'

    return render_template('test_results.html', results=results, graph=graph, recommendations=recommendations, counseling={'stream': stream, 'reason': latest_result['counseling_reason'], 'color': stream_color})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)