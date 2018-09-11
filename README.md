# Retrolection

1. Télécharger et installer python 3:
https://www.python.org/downloads/

2. Installer le module python "Pillow" en tapant la commande:
```
pip install Pillow
```

3. Modifier le fichier config.ini pour renseigner la clé API (la méthode pour obtenir une clé API est détaillée ici:https://github.com/ThorAsgardDev/xsplit_retrolection_extension)

4. Double cliquer sur le fichier "retrolection.pyw"


Côté XSplit:

Ajouter des sources "text" en utilisant le custom script "Load Text from Local File".
Utiliser les file path suivants:

```
Nom du jeu: <appli retrolection>/text-files/game.txt
L'indicateur de progression: <appli retrolection>/text-files/progression.txt
Nom du viewer don: <appli retrolection>/text-files/viewer-don.txt
Nom du viewer sub: <appli retrolection>/text-files/viewer-sub.txt
Timer: <appli retrolection>/text-files/timer.txt
```

Pour le timer il y a un bug côté XSplit. On peut le contourner en utilisant la manip suivante:

Pour la source "text" du timer, au lieu d'utiliser le custom script "Load Text from Local File" il faut utiliser un "Block Template" et copier le contenu du script:
```
<appli retrolection>/xsplit-script/update-timer-script.js
```