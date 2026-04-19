# My Workout App

A simple web application built with Flask for tracking workouts.

## Setup and Installation

1. **Clone or download** the project to your local machine.

2. **Navigate** to the project directory:
   ```
   cd my_workout_app
   ```

3. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```
   python app.py
   ```

5. **Open your browser** and go to `http://localhost:5000` to access the app.

## Features

- Landing page with navigation to workout tracker
- Workout tracking page (currently a placeholder)

## Project Structure

```
my_workout_app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css      # Stylesheet
│   └── videos/            # Directory for workout videos
└── templates/
    ├── index.html         # Landing page
    └── workout.html       # Workout tracking page
```

## Usage

- Visit the home page to get started.
- Click "Start Your Workout" to go to the tracking page.
- Add your workout videos to the `static/videos/` directory.

## Troubleshooting

- Ensure Python 3.7+ is installed.
- If you encounter import errors, try creating a virtual environment:
  ```
  python -m venv venv
  venv\Scripts\activate  # On Windows
  pip install -r requirements.txt
  ```