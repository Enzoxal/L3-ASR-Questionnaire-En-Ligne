Projet: Questionnaire en ligne 

Membre du groupe: 
ZEKHMI	Enzo
GALINIER	Thomas
GUERMOUR	Said	
HETTAK	Hani

Noyau minimal: 
#1-Chargement des questionnaires à partir d'un fichier JSON
#2-Accès via une URL
#3-Affichage du questionnaire ( dépend de #2 )
#4-Valider les réponses (dépend de #3)
#5-Enregistrer les réponses (dépend de #4)

Fonctionnalité complémentaire:
#6-Authentification d'accès
#7-Affichage des questionnaire (coté administrateur)
#8-Récuperer les résultats   (coté administrateur)
#9-Ajouter ses propres questionnaires (coté adminstrateur)
#10-Créer son propre questionnaire (coté administrateur) 
#11-Supprimer un questionnaire
#12-Interface administrateur / utilisateur 
  

Ordre de priorité: 
Noyau minimal 

---------------------------------------------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------------------------------------

(/!\ POUR UNE MEILLEUR LISIBILITÉ, IL VAUT MIEUX TÉLÉCHARGER LE README /!\)

Bibliothèque :
-Fask  (→ jinja2)
-Flask-Login
-Flask-SQLALchemy
-Werkzeug
-JSON
-CSV
-os
-datetime
-re
-Boostrap4
-Bibliotheque standard venant de python (datetime...)

Structure :
onlineQuiz → Dossier global
|→ Main → Entrée de l’application
|→ instance→ dossier contenant un fichier (fichier qui contient la base de donnée)
	|→ database.db
|→ website → dossier contenant tous les codes.
	|→ _pycache_ → dossier automatique correspondant au cache python, afin d’avancer l’execution
	|→ questionnaire → contient les questionnaire quee le site affichera (import, creation ou inclusion)
	|→ questionnaires → ancien dossiers ayant la meme fonctionnalité au début du projet, devenu obsolete 
	|→ results → dossier ou seront enregistrer les résultat des questionnaire (en csv)
	|→ static → dossier 
		|→ index.js → fichier prévu pour des fonctionnalité au début du projet mais rendu obsolete une fois avancé dans le projet
	| template → dossier contenant les template  (jinja2 ) en html diviser en plusieurs fichier pour chaque élément/page/fonctionnalité du site nécessaire (le fichier quizz est obsolete et vide )
	|→ init.py → initialiser l’application Flask
	|→ auth.py → gere les connexion, deconnexion creation de compte …
	|→ models.py → permet de créer et gerer les données de la base de donnée 
	|→ view.py → Gère les route url et les principale fonctionnalité de notre site 

Répartition du travail :
Hani Hettak → init.py, view.py → ligne : début - 162 (fonctionnalité : gestion des format, type de réponse, fonctionnement d ‘un questionnaire etc ...) , html
Thomas Galinier →model.py ,view..py→ ligne : 163- 314 (fonctionnalité : afffichage questionnaire utilisateur, type de réponse, sauvegarde des réponse format csv…  )  , html
Said Guermour → base de donnée, auth.py (connexion, deconnexion , inscription) , html
Enzo Zekhmi → view.py ligne 315 – fin  → fonctionnalité administrateur ( affichage des questionnaires, import, suppression, affichage des resultats, récuperation des résultats, creation des questionnaires...), html
