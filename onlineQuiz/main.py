from website import create_app

app = create_app()

if __name__ == '__main__': # seulement si ce fichier est exécuté directement
    app.run(debug=True) # démarrer le serveur Flask en mode debug  