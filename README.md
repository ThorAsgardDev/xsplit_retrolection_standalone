# Retrolection


## Côté appli Retrolection

1. Télécharger et installer python 3:
https://www.python.org/downloads/

2. Installer les dépendances python:
```
pip install -r requirements.txt
```

3. Récupérer un fichier de credentials pour les acces au gdoc:

Suivre les instructions pour un "bot account" indiquées ici: https://docs.gspread.org/en/latest/oauth2.html

Nommer le fichier:
```
retrolection-creds.json
```

4. Double cliquer sur le fichier "retrolection.pyw"


## Côté OBS

Utiliser les fichiers suivants:

```
Nom du jeu: <appli retrolection>/text-files/game.txt
L'indicateur de progression de la console: <appli retrolection>/text-files/progression-console.txt
L'indicateur de progression totale Retrolection: <appli retrolection>/text-files/progression-total.txt
Timer du jeu: <appli retrolection>/text-files/timer-game.txt
Timer Retrolection: <appli retrolection>/text-files/timer-total.txt
```

Pour la jaquette utiliser le fichier suivant:

```
<appli retrolection>/img-files/cover.png
```

La jaquette et toutes les valeurs seront mises à jour lors d'un clique sur le bouton "Envoyer vers OBS"
