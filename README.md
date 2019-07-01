# Retrolection

1. Télécharger et installer python 3:
https://www.python.org/downloads/

2. Installer le module python "Pillow" en tapant la commande:
```
pip install Pillow
```

3. Modifier le fichier config.ini pour renseigner les valeurs:
   - GDOC_API_KEY (la méthode pour obtenir une clé API est détaillée ici: https://github.com/ThorAsgardDev/xsplit_retrolection_extension)
   - IGDB_API_KEY (s'inscrire gratuitement ici: https://api.igdb.com/)

4. Double cliquer sur le fichier "retrolection.pyw"


Côté XSplit:

Ajouter des sources "text" en utilisant le custom script "Load Text from Local File".
Utiliser les file path suivants:

```
Nom du jeu: <appli retrolection>/text-files/game.txt
L'indicateur de progression de la console: <appli retrolection>/text-files/progression-console.txt
L'indicateur de progression totale Retrolection: <appli retrolection>/text-files/progression-total.txt
Nom du viewer don: <appli retrolection>/text-files/viewer-don.txt
Nom du viewer sub: <appli retrolection>/text-files/viewer-sub.txt
Défi don: <appli retrolection>/text-files/challenge-don.txt
Défi sub: <appli retrolection>/text-files/challenge-sub.txt
Timer du jeu: <appli retrolection>/text-files/timer-game.txt
Timer Retrolection: <appli retrolection>/text-files/timer-total.txt
```

Pour les timers il y a un bug côté XSplit. On peut le contourner en utilisant la manip suivante:

Pour la source "text" d'un timer, au lieu d'utiliser le custom script "Load Text from Local File" il faut utiliser un "Block Template" et copier le contenu du script:
```
<appli retrolection>/xsplit-script/update-timer-script.js
```

Pour la jaquette, il faut ajouter une source de type "General Widgets -> Image Slideshow"
Dans la configuration de la source, cocher la case "Auto-refresh images" et ajouter le fichier suivant:

```
<appli retrolection>/img-files/cover.png
```

La jaquette sera mise à jour lors d'un clique sur le bouton "Envoyer les valeurs vers XSplit"
