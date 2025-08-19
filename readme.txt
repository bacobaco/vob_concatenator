DVD => MP4 Concatenator for Youtube
(Requirements: ffmpeg.exe - website https://ffmpeg.org/download.html)

version v1beta = version avec option de réencoder chaque vob en ts avec le son compatible youtube puis concat MP4
version v1.01b = quelques corrections mineures
version v2b = ajout d'une amélioration pour les couleurs pour youtube (assombrissement constaté de certaine vidéo après upload de la vidéo):
                    ✓ Forçage de l'espace colorimétrique
                    ✓ Forçage du range couleur limité (16-235)
                    ✓ Métadonnées optimisées pour YouTube
version V3 =  Ajout de deux options pour améliorer le gamma et un boost luminosité, qui réencode la vidéo (PRUDENCE!)
                [Ajout automatique du filtre yadif avant toutes corrections visuelles, seulement si une correction gamma/luminosité est activée.
                Ceci évite l’effet d’entrelacement (peigne) lors du réencodage.
                Les options audio/vidéo YouTube restent inchangées.
                Aucun effet sur le pipeline lorsqu’il n’y a pas de traitement visuel : la copie directe de la vidéo reste inchangée.]

===========  RAPPEL pour créer un exécutable Windows à partir d'un fichier Python unique  =======
Pour créer un exécutable Windows à partir d'un fichier Python unique, voici les méthodes les plus simples :
PyInstaller (recommandé)

Installation :
pip install pyinstaller

Création de l'exécutable :
pyinstaller --onefile --icon=vob_concatenator.ico vob_concatenator.py

L'exécutable sera dans le dossier dist/. Options utiles :
--onefile : un seul fichier exécutable
--windowed : pas de console (pour les GUI)
--icon=icone.ico : ajouter une icône
==================================================================================================