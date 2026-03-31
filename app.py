import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DB = os.path.join(os.path.dirname(__file__), "todos.db")
PRIORITIES = ["high", "medium", "low"]


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                task     TEXT NOT NULL,
                priority TEXT NOT NULL DEFAULT 'medium',
                done     INTEGER NOT NULL DEFAULT 0
            )
        """)


@app.route("/")
def index():
    order = {"high": 0, "medium": 1, "low": 2}
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM todos").fetchall()
    todos = sorted(rows, key=lambda t: (t["done"], order.get(t["priority"], 1)))
    return render_template("index.html", todos=todos)


@app.route("/add", methods=["POST"])
def add():
    task = request.form.get("task", "").strip()
    priority = request.form.get("priority", "medium")
    if task and priority in PRIORITIES:
        with get_db() as conn:
            conn.execute("INSERT INTO todos (task, priority) VALUES (?, ?)", (task, priority))
    return redirect(url_for("index"))


@app.route("/done/<int:idx>", methods=["POST"])
def done(idx):
    with get_db() as conn:
        row = conn.execute("SELECT done FROM todos WHERE id = ?", (idx,)).fetchone()
        if row:
            conn.execute("UPDATE todos SET done = ? WHERE id = ?", (0 if row["done"] else 1, idx))
    return redirect(url_for("index"))


@app.route("/delete/<int:idx>", methods=["POST"])
def delete(idx):
    with get_db() as conn:
        conn.execute("DELETE FROM todos WHERE id = ?", (idx,))
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
