from flask import Blueprint, render_template, current_app # Ajout de current_app
from flask_login import login_required, current_user
import json
import os

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)

@views.route('/quiz')
@login_required
def quiz():
    #Construire le chemin vers le fichier JSON
    filename = os.path.join(current_app.root_path, 'questions.json')

    #Ouvrir et lire le fichier
    data = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        print("Erreur : Le fichier questions.json est introuvable.")

    # 3. Envoyer les données dans la page HTML
    return render_template("quiz.html", user=current_user, questions=data)