from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Tell Flask to use a local SQLite file named 'workouts.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workouts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database tool
db = SQLAlchemy(app)

# --- Define the Database Table using a Python Class ---
class WorkoutLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_type = db.Column(db.String(50), nullable=False)     # e.g., 'push', 'pull', 'base'
    exercise_name = db.Column(db.String(100), nullable=False)
    set_number = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=True)             # Nullable because Dead Bugs are time-based!
    weight = db.Column(db.Float, nullable=True)
    duration = db.Column(db.Integer, nullable=True)         # Seconds
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Log: {self.day_type} - {self.exercise_name} Set {self.set_number}>"

# Create the actual database file and tables if they don't exist yet
with app.app_context():
    db.create_all()

# --- Your Existing Routes ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/workout/<workout_type>')
def workout_day(workout_type):
    return render_template('workout.html', workout_type=workout_type)

@app.route('/history')
def history():
    # Fetch all logs from the database, ordered by newest first
    all_logs = WorkoutLog.query.order_by(WorkoutLog.timestamp.desc()).all()
    
    # Send the logs to a new HTML page
    return render_template('history.html', logs=all_logs)

@app.route('/log_set', methods=['POST'])
def log_set():
    data = request.json
    new_log = WorkoutLog(
        day_type=data.get('day_type'),
        exercise_name=data.get('exercise_name'),
        set_number=data.get('set_number'),
        reps=data.get('reps'),
        weight=data.get('weight'),
        duration=data.get('duration')
    )
    db.session.add(new_log)
    db.session.commit()
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(debug=True)