"""
startup.py — auto-runs data generation + cleaning + DB setup on first launch.
Called from app.py before anything else.
"""
import os

if not os.path.exists("data/cleaned_literacy.csv"):
    print("First run — generating data...")
    os.makedirs("data", exist_ok=True)
    exec(open("generate_data.py").read())
    exec(open("data_processing.py").read())

if not os.path.exists("data/literacy.db"):
    exec(open("database_setup.py").read())