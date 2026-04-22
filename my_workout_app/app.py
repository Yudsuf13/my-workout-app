from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workouts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class WorkoutLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_type = db.Column(db.String(50), nullable=False)
    exercise_name = db.Column(db.String(100), nullable=False)
    set_number = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    duration = db.Column(db.Integer, nullable=True)
    comment = db.Column(db.Text, nullable=True)          # NEW
    timestamp = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Log: {self.day_type} - {self.exercise_name} Set {self.set_number}>"


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/workout/<workout_type>')
def workout_day(workout_type):
    # Validate workout type
    if workout_type not in ['push', 'pull', 'base']:
        return "Invalid workout type", 404
    return render_template('workout.html', workout_type=workout_type)

@app.route('/history')
def history():
    all_logs = WorkoutLog.query.order_by(WorkoutLog.timestamp.desc()).all()
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
        duration=data.get('duration'),
        comment=data.get('comment')          # NEW
    )
    db.session.add(new_log)
    db.session.commit()
    return jsonify({"status": "success"}), 200

@app.route('/clear_history', methods=['POST'])
def clear_history():
    try:
        num_deleted = db.session.query(WorkoutLog).delete()
        db.session.commit()
        return jsonify({"status": "success", "deleted": num_deleted}), 200
    except:
        db.session.rollback()
        return jsonify({"status": "error"}), 500
    
@app.route('/update_log/<int:log_id>', methods=['POST'])
def update_log(log_id):
    log = WorkoutLog.query.get_or_404(log_id)
    data = request.json
    
    # Update fields if provided (allow null to clear)
    if 'reps' in data:
        log.reps = data['reps']
    if 'weight' in data:
        log.weight = data['weight']
    if 'duration' in data:
        log.duration = data['duration']
    if 'comment' in data:
        log.comment = data['comment']
    
    db.session.commit()
    return jsonify({"status": "success"}), 200

@app.route('/delete_log/<int:log_id>', methods=['POST'])
def delete_log(log_id):
    log = WorkoutLog.query.get_or_404(log_id)
    db.session.delete(log)
    db.session.commit()
    return jsonify({"status": "success"}), 200

# New model
class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_start_date = db.Column(db.Date, nullable=True)

    @staticmethod
    def get_start_date():
        setting = Settings.query.first()
        return setting.program_start_date if setting else None

    @staticmethod
    def set_start_date(date):
        setting = Settings.query.first()
        if not setting:
            setting = Settings()
            db.session.add(setting)
        setting.program_start_date = date
        db.session.commit()

# Add this route for setting start date
@app.route('/set_start_date', methods=['POST'])
def set_start_date():
    data = request.json
    date_str = data.get('start_date')
    if date_str:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        Settings.set_start_date(date_obj)
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/get_start_date', methods=['GET'])
def get_start_date():
    date = Settings.get_start_date()
    return jsonify({"start_date": date.isoformat() if date else None})

from datetime import timedelta

@app.route('/calendar')
def calendar_view():
    return render_template('calendar.html')

@app.route('/get_week_data')
def get_week_data():
    # Expect a query param ?date=YYYY-MM-DD (the reference date for the week)
    ref_date_str = request.args.get('date')
    if ref_date_str:
        ref_date = datetime.strptime(ref_date_str, '%Y-%m-%d').date()
    else:
        ref_date = datetime.now().date()   # was datetime.utcnow
    
    # Find Monday of that week
    start_of_week = ref_date - timedelta(days=ref_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # Get all logs within that week
    logs = WorkoutLog.query.filter(
        db.func.date(WorkoutLog.timestamp) >= start_of_week,
        db.func.date(WorkoutLog.timestamp) <= end_of_week
    ).all()
    
    # Build a dict mapping date -> list of logs (or just workout types)
    week_data = {}
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        week_data[day.isoformat()] = {
            'has_workout': False,
            'day_type': None,
            'first_log_time': None
        }
    
    for log in logs:
        day_str = log.timestamp.date().isoformat()
        if not week_data[day_str]['has_workout']:
            week_data[day_str]['has_workout'] = True
            week_data[day_str]['day_type'] = log.day_type
            week_data[day_str]['first_log_time'] = log.timestamp.strftime('%I:%M %p')
    
    return jsonify({
        'week_start': start_of_week.isoformat(),
        'week_end': end_of_week.isoformat(),
        'days': week_data
    })

@app.route('/get_day_details/<date_str>')
def get_day_details(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    logs = WorkoutLog.query.filter(
        db.func.date(WorkoutLog.timestamp) == date_obj
    ).order_by(WorkoutLog.timestamp).all()
    
    # Group by exercise
    details = []
    for log in logs:
        details.append({
            'id': log.id,
            'exercise': log.exercise_name,
            'set': log.set_number,
            'reps': log.reps,
            'weight': log.weight,
            'duration': log.duration,
            'comment': log.comment,
            'time': log.timestamp.strftime('%I:%M %p')
        })
    
    return jsonify({'logs': details})

# Add near the top after imports
from datetime import datetime, timedelta, date

def get_cycle_day(target_date):
    """Returns 'push', 'pull', 'base', or 'break' for a given date based on program start."""
    start = Settings.get_start_date()
    if not start:
        return None
    delta_days = (target_date - start).days
    if delta_days < 0:
        return None
    # Cycle: 0=push, 1=break, 2=pull, 3=break, 4=base, 5=break, then repeats
    cycle_day = delta_days % 6
    mapping = {
        0: 'push',
        1: 'break',
        2: 'pull',
        3: 'break',
        4: 'base',
        5: 'break'
    }
    return mapping[cycle_day]

@app.route('/get_cycle_info')
def get_cycle_info():
    # For a specific date? We'll accept a date param
    date_str = request.args.get('date')
    if date_str:
        target = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        target = datetime.now().date()
    workout_type = get_cycle_day(target)
    return jsonify({
        'date': target.isoformat(),
        'workout_type': workout_type,
        'is_break': workout_type == 'break' if workout_type else None
    })

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)