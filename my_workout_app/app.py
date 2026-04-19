from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# The <workout_type> part acts as a variable!
@app.route('/workout/<workout_type>')
def workout_day(workout_type):
    # This passes the 'push', 'pull', or 'base' variable directly into your HTML
    return render_template('workout.html', workout_type=workout_type)

if __name__ == '__main__':
    app.run(debug=True)