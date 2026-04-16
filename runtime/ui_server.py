# FILE: runtime\ui_server.py

from flask import Flask
import json
import os

app = Flask(__name__)

def load_json(path):
    try:
        with open(path, encoding="utf-8-sig") as f:
            return json.load(f)
    except:
        return {}

@app.route("/")
def dashboard():

    timeline = open("runtime/index/event_timeline.csv", encoding="utf-8-sig").read()
    intent = load_json("runtime/intent_memory.json")

    return f"""
    <h1>MoCKA Control Panel</h1>

    <h2>Current Intent</h2>
    <pre>{intent.get("history", [])[-1:]}</pre>

    <h2>System Status</h2>
    <pre>
    Total Events: {len(timeline.splitlines())}
    </pre>

    <h2>Controls</h2>
    <a href="/run">▶ Execute</a><br>
    <a href="/mutate">🔁 Mutate Intent</a><br>
    <a href="/evaluate">📊 Evaluate Intent</a><br>
    <a href="/select">🎯 Select Best Intent</a><br>

    <h2>Timeline</h2>
    <pre>{timeline[-2000:]}</pre>
    """

@app.route("/run")
def run():
    os.system("python runtime/executor.py")
    return "<h3>EXECUTED</h3><a href='/'>Back</a>"

@app.route("/mutate")
def mutate():
    os.system("python runtime/intent_mutator.py")
    return "<h3>MUTATED</h3><a href='/'>Back</a>"

@app.route("/evaluate")
def evaluate():
    os.system("python runtime/intent_evaluator.py")
    return "<h3>EVALUATED</h3><a href='/'>Back</a>"

@app.route("/select")
def select():
    os.system("python runtime/intent_selector.py")
    return "<h3>SELECTED</h3><a href='/'>Back</a>"

if __name__ == "__main__":
    print("START http://localhost:5000")
    app.run(port=5000)
