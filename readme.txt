DVD => MP4 Concatenator for Youtube

version v1alpha = premiere version => concaténation des fichiers vob du dvd
version v1beta = version avec option de réencoder chaque vob en ts avec le son compatible youtube puis concat MP4


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