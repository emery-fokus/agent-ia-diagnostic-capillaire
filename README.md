# Agent IA de diagnostic capillaire

Une petite application qui pose des questions sur tes cheveux, puis te propose
un diagnostic, des produits trouvés sur internet et une routine, grâce à une IA.

Ce guide est écrit pour quelqu'un qui n'a jamais installé de projet Python.
Suis les étapes dans l'ordre, sous Windows.

## 1. Installer Python (si ce n'est pas déjà fait)

Va sur [python.org/downloads](https://www.python.org/downloads/) et installe
la dernière version. Pendant l'installation, coche bien la case
**"Add python.exe to PATH"**.

## 2. Ouvrir le projet dans un terminal

- Ouvre le dossier du projet dans l'explorateur de fichiers.
- Dans la barre d'adresse du dossier, tape `cmd` puis appuie sur Entrée.
  Un terminal s'ouvre directement dans le bon dossier.

## 3. Créer l'environnement virtuel

Un environnement virtuel est un petit dossier isolé qui contiendra les
programmes nécessaires au projet, sans toucher au reste de l'ordinateur.

```bash
python -m venv venv
```

## 4. Activer l'environnement virtuel

```bash
venv\Scripts\activate
```

Si ça fonctionne, tu dois voir `(venv)` apparaître au début de la ligne dans
le terminal. Il faudra refaire cette commande à chaque fois que tu rouvres
un terminal pour travailler sur le projet.

## 5. Installer les dépendances

Les dépendances sont les programmes dont l'application a besoin pour
fonctionner (Streamlit, Groq, Tavily...).

```bash
pip install -r requirements.txt
```

## 6. Créer les clés API (gratuites)

L'application a besoin de deux clés API gratuites pour fonctionner :

### Clé Groq (pour que l'IA rédige le diagnostic)

1. Va sur [console.groq.com](https://console.groq.com) et crée un compte gratuit.
2. Dans le menu, va dans **API Keys**, puis clique sur **Create API Key**.
3. Copie la clé affichée (elle commence par `gsk_...`). Attention, elle ne
   s'affiche qu'une seule fois.

### Clé Tavily (pour chercher de vrais produits sur internet)

1. Va sur [tavily.com](https://tavily.com) et crée un compte gratuit.
2. Une clé API est générée automatiquement sur ton tableau de bord
   (elle commence par `tvly-...`). Copie-la.
3. Le compte gratuit donne 1000 recherches par mois, largement suffisant
   pour ce projet.

## 7. Créer le fichier .env

1. Fais une copie du fichier `.env.example` et renomme-la en `.env`.
2. Ouvre ce fichier `.env` avec un éditeur de texte (le Bloc-notes par exemple).
3. Complète-le avec tes deux clés, comme ceci :

```
GROQ_API_KEY=gsk_ta_cle_groq_ici
TAVILY_API_KEY=tvly_ta_cle_tavily_ici
```

4. Enregistre et ferme le fichier. **Ne partage jamais ce fichier** et ne le
   mets jamais sur GitHub (le fichier `.gitignore` du projet l'exclut déjà
   automatiquement).

## 8. Lancer l'application

```bash
streamlit run app.py
```

Une page va s'ouvrir automatiquement dans ton navigateur. Si elle ne s'ouvre
pas seule, copie l'adresse affichée dans le terminal (quelque chose comme
`http://localhost:8501`) dans ton navigateur.

## 9. Arrêter l'application

Retourne dans le terminal et appuie sur `Ctrl + C`.
