from flask import Flask, Response, g, abort
import sqlite3
import csv
import io

app = Flask(__name__)
DATABASE = "questionnaire.db"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def get_questions(questionnaire_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        SELECT id, key
        FROM question
        WHERE questionnaire_id = ?
        ORDER BY id ASC
    """, (questionnaire_id,))
    return cur.fetchall()

def get_raw_rows(questionnaire_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        SELECT
            s.id AS submission_id,
            s.submitted_at AS submitted_at,
            q.key AS question_key,
            a.value AS answer_value
        FROM submission s
        LEFT JOIN answer a ON a.submission_id = s.id
        LEFT JOIN question q ON q.id = a.question_id
        WHERE s.questionnaire_id = ?
        ORDER BY s.id ASC
    """, (questionnaire_id,))
    return cur.fetchall()

@app.route("/admin/questionnaire/<int:questionnaire_id>/results.csv")
def export_csv(questionnaire_id):
    questions = get_questions(questionnaire_id)
    if not questions:
        abort(404)

    keys = [q["key"] for q in questions]
    raw = get_raw_rows(questionnaire_id)

    subs = {}
    for r in raw:
        sid = r["submission_id"]
        if sid not in subs:
            subs[sid] = {
                "submitted_at": r["submitted_at"],
                "answers": {k: "" for k in keys}
            }
        if r["question_key"] is not None:
            subs[sid]["answers"][r["question_key"]] = r["answer_value"] or ""

    out = io.StringIO()
    w = csv.writer(out, delimiter=";")
    w.writerow(["submission_id", "submitted_at"] + keys)

    for sid, data in subs.items():
        row = [sid, data["submitted_at"]] + [data["answers"][k] for k in keys]
        w.writerow(row)

    return Response(
        out.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename=questionnaire_{questionnaire_id}.csv"
        }
    )

if __name__ == "__main__":
    app.run(debug=True)
