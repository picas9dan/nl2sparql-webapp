# Flask app

## Local setup 

1. Create a virtual environment for dependency management and activate it.

   ```
   python3 -m venv .venv
   source .venv/bin/activate
   ```

1. Install dependencies `pip install -r requirements.txt`.

1. Start the development server in debug mode (app is automatically reloaded upon code changes) `uvicorn main:app --reload`. The app will be running at `localhost:8000`.
