1. Create a virtual environment inside the "WIFI-PERFORMANCE-ANALYSIS" folder -> "python -m venv .venv"
2. activate it -> ".venv/Scripts/activate" (for windows)
            if error is there then run "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser" then activate again
3. install dependencies -> "pip install -r requirements.txt"

4. to add some dummy data in the DB run "python dummyDatabase.py" 
    (   !!! WARNING
        This action will delete all the data in the database & write some dummy data in the DB"
    )
5. run the app -> "flask run"
