
Le projet permet de télécharger un fichier depuis Google Drive et de l'utiliser avec Ollama pour discuter avec l'IA du contenu du fichier. Cela peut inclure des fichiers PDF, des documents texte et des fichiers JSON.
Il faut que Python soit installé sur votre machine. Ce projet a été testé avec Python 3.12.

Setup :

- pip install -r requirements.txt
- Installer Ollama (https://ollama.com/download)
- ollama pull llama3
- ollama pull mxbai-embed-large

Commands :
- python3 drive.py
    Accès au google drive en accès public.
    Téléchargement du fichier défini dans le bulb du drive.py vers le fichier local_exemple.pdf.
- python3 localrag.py
    Discussion avec Ollama sur le pdf téléchargé.

Configuration de la créativité d'Ollama :
- ollama run llama3
- /set parameter temperature <valeur>

Fini ? :
- quit
