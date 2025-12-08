from flask import (
    Blueprint,
    render_template,
    current_app,
    request,
    redirect,
    url_for,
    flash,
    abort,
    send_from_directory,
)
from flask_login import login_required, current_user
import json
import os
import csv
from datetime import datetime
from werkzeug.utils import secure_filename

views = Blueprint('views', __name__)

ALLOWED_EXTENSIONS = {'json'}


@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)


# ---------- OUTILS ----------

def load_questions(qid: str):
    """Charge la liste de questions pour un questionnaire donné (fichier JSON)."""
    filename = os.path.join(current_app.root_path, 'questionnaire', f'{qid}.json')
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return None


def save_answers(qid: str, questions, answers: dict):
    """Enregistre les réponses dans un CSV results/<qid>.csv."""
    results_dir = os.path.join(current_app.root_path, 'results')
    os.makedirs(results_dir, exist_ok=True)

    csv_path = os.path.join(results_dir, f'{qid}.csv')

    fieldnames = ['date', 'user_id', 'user_name', 'user_email'] + [
        q['key'] for q in questions
    ]

    file_exists = os.path.exists(csv_path)

    with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')

        if not file_exists:
            writer.writeheader()

        row = {
            'date': datetime.now().strftime("%d/%m/%Y"),
            'user_id': current_user.id,
            'user_name': current_user.first_name,
            'user_email': current_user.email,
        }
        row.update(answers)
        writer.writerow(row)


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------- QUESTIONNAIRES UTILISATEUR ----------

@views.route('/q/<qid>', methods=['GET', 'POST'])
@login_required
def questionnaire(qid):
    questions = load_questions(qid)

    if questions is None:
        flash(f"Questionnaire '{qid}' introuvable.", "error")
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        answers = {}
        for q in questions:
            key = q['key']
            user_answer = request.form.get(key, "")
            answers[key] = user_answer

        save_answers(qid, questions, answers)
        flash("Merci ! Vos réponses ont été enregistrées.", "success")
        return redirect(url_for('views.home'))

    return render_template(
        "quiz.html",
        user=current_user,
        questions=questions,
        qid=qid
    )


@views.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    # alias vers le questionnaire "questions.json"
    return questionnaire('questions')


# ---------- ADMIN : LISTE DES QUESTIONNAIRES ----------

@views.route('/admin/questionnaires')
@login_required
def admin_questionnaires():
    if not current_user.is_admin:
        abort(403)

    q_dir = os.path.join(current_app.root_path, 'questionnaire')
    questionnaires = []

    if os.path.isdir(q_dir):
        for fname in os.listdir(q_dir):
            if fname.endswith('.json'):
                qid = os.path.splitext(fname)[0]
                csv_path = os.path.join(current_app.root_path, 'results', f'{qid}.csv')
                has_results = os.path.exists(csv_path)

                questionnaires.append({
                    'id': qid,
                    'filename': fname,
                    'has_results': has_results,
                })

    return render_template(
        "admin_questionnaires.html",
        user=current_user,
        questionnaires=questionnaires
    )


# ---------- ADMIN : VOIR LES RÉSULTATS D'UN QUESTIONNAIRE ----------

@views.route('/admin/questionnaires/<qid>/results')
@login_required
def admin_questionnaire_results(qid):
    if not current_user.is_admin:
        abort(403)

    results_dir = os.path.join(current_app.root_path, 'results')
    csv_path = os.path.join(results_dir, f'{qid}.csv')

    rows = []
    fieldnames = []

    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            fieldnames = reader.fieldnames or []
            for row in reader:
                rows.append(row)
    else:
        flash("Aucun résultat trouvé pour ce questionnaire.", "info")

    return render_template(
        "admin_results.html",
        user=current_user,
        qid=qid,
        fieldnames=fieldnames,
        rows=rows
    )


# ---------- ADMIN : TÉLÉCHARGER LES RÉSULTATS (CSV) ----------

@views.route('/admin/questionnaires/<qid>/results/download')
@login_required
def admin_download_results(qid):
    if not current_user.is_admin:
        abort(403)

    results_dir = os.path.join(current_app.root_path, 'results')
    csv_filename = f"{qid}.csv"
    csv_path = os.path.join(results_dir, csv_filename)

    if not os.path.exists(csv_path):
        flash("Aucun fichier de résultats à télécharger pour ce questionnaire.", "info")
        return redirect(url_for('views.admin_questionnaire_results', qid=qid))

    return send_from_directory(
        results_dir,
        csv_filename,
        as_attachment=True,
        download_name=f"{qid}_results.csv"
    )


# ---------- ADMIN : UPLOAD D'UN QUESTIONNAIRE JSON (#9) ----------

@views.route('/admin/questionnaires/upload', methods=['GET', 'POST'])
@login_required
def admin_upload_questionnaire():
    if not current_user.is_admin:
        abort(403)

    if request.method == 'POST':
        file = request.files.get('file')

        if not file or file.filename == '':
            flash("Aucun fichier sélectionné.", "error")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Seuls les fichiers .json sont autorisés.", "error")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        q_dir = os.path.join(current_app.root_path, 'questionnaire')
        os.makedirs(q_dir, exist_ok=True)
        save_path = os.path.join(q_dir, filename)
        file.save(save_path)

        flash(f"Questionnaire '{filename}' importé avec succès.", "success")
        return redirect(url_for('views.admin_questionnaires'))

    return render_template("admin_upload.html", user=current_user)


# ---------- ADMIN : CRÉATION D'UN QUESTIONNAIRE (questions + options dynamiques) ----------

@views.route('/admin/questionnaires/create', methods=['GET', 'POST'])
@login_required
def admin_create_questionnaire():
    if not current_user.is_admin:
        abort(403)

    if request.method == 'POST':
        qid = request.form.get('qid', '').strip()
        if not qid:
            flash("L'identifiant du questionnaire est obligatoire.", "error")
            return redirect(request.url)

        # On détecte dynamiquement tous les index de questions présents
        indices = set()
        for field in request.form.keys():
            if field.startswith('key_') or field.startswith('label_') or field.startswith('type_'):
                try:
                    idx = int(field.split('_')[1])
                    indices.add(idx)
                except ValueError:
                    pass

        questions = []
        for idx in sorted(indices):
            key = request.form.get(f'key_{idx}', '').strip()
            label = request.form.get(f'label_{idx}', '').strip()
            desc = request.form.get(f'desc_{idx}', '').strip()
            qtype = request.form.get(f'type_{idx}', 'text')
            required = request.form.get(f'required_{idx}') == 'on'

            # Si la question est complètement vide, on ignore
            if not key and not label:
                continue

            q = {
                "id": idx,
                "key": key,
                "label": label,
                "description": desc,
                "type": qtype,
                "required": required
            }

            # Options multiples : option_<idx>_<optIndex>
            if qtype == 'choice':
                options = []
                for form_key, value in request.form.items():
                    prefix = f"option_{idx}_"
                    if form_key.startswith(prefix):
                        val = value.strip()
                        if val:
                            options.append(val)

                if options:
                    q["options"] = options

            questions.append(q)

        if not questions:
            flash("Aucune question valide n'a été définie.", "error")
            return redirect(request.url)

        q_dir = os.path.join(current_app.root_path, 'questionnaire')
        os.makedirs(q_dir, exist_ok=True)
        json_path = os.path.join(q_dir, f"{qid}.json")

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)

        flash(f"Questionnaire '{qid}' créé avec succès.", "success")
        return redirect(url_for('views.admin_questionnaires'))

    return render_template(
        "admin_create.html",
        user=current_user,
    )
