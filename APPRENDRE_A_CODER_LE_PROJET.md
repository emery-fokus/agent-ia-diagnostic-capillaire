# Apprendre à coder ce projet, étape par étape

Ce document est comme un petit cours particulier. Il ne se contente pas
d'expliquer le code déjà écrit : il te montre, étape par étape, **comment on
construirait ce projet à partir de rien**, comme si un professeur était
assis à côté de toi. À la fin, tu comprendras non seulement ce que fait
`app.py`, mais aussi *pourquoi* il est écrit comme ça et *comment* tu
pourrais toi-même écrire quelque chose de semblable.

Tu peux suivre ce cours en tapant toi-même le code dans un nouveau fichier
(par exemple `exercice.py`), étape après étape, et en lançant
`streamlit run exercice.py` à chaque étape pour voir le résultat évoluer.

---

## Partie 0 — Le vocabulaire de base (2 minutes)

Avant de commencer, voici les quelques mots qu'on va utiliser tout le long.
Pas besoin de les apprendre par cœur, on les reverra en pratique.

- **Une variable** : une boîte avec un nom, qui garde une valeur.
  Exemple : `prenom = "Awa"` crée une boîte nommée `prenom` qui contient le
  texte `"Awa"`.
- **Une fonction** : une petite machine à qui on donne des ingrédients
  (des *paramètres*), et qui nous rend un résultat. On l'écrit une fois, et
  on peut s'en servir autant de fois qu'on veut.
- **Une liste** : une boîte qui contient plusieurs valeurs à la suite,
  entre crochets. Exemple : `fruits = ["pomme", "banane"]`.
- **Une condition (`if`)** : une façon de dire "si telle chose est vraie,
  fais ceci, sinon fais autre chose".
- **Une boucle (`for`)** : une façon de répéter une action pour chaque
  élément d'une liste, un par un.
- **Importer une bibliothèque** : utiliser du code déjà écrit par d'autres
  personnes (par exemple pour créer une page web, ou parler à une IA), au
  lieu de tout réécrire soi-même.

---

## Partie 1 — Préparer le terrain

On crée un nouveau fichier Python, et on installe les outils (les
**bibliothèques**) dont on va avoir besoin : `streamlit` pour la page web,
`groq` pour parler à l'IA, `tavily-python` pour chercher sur internet, et
`python-dotenv` pour lire les clés API en toute sécurité.

```bash
pip install streamlit groq tavily-python python-dotenv
```

Puis, en haut du fichier, on dit à Python qu'on va utiliser ces outils :

```python
import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient
```

`import os` n'a rien à installer : c'est un outil déjà fourni avec Python,
qui sert ici à lire les clés API cachées dans un fichier séparé.

---

## Partie 2 — Afficher quelque chose à l'écran

Avant de faire quoi que ce soit de compliqué, on vérifie que Streamlit
fonctionne, en affichant juste un titre :

```python
st.title("Agent IA de diagnostic capillaire")
```

Lance `streamlit run exercice.py` dans le terminal : une page web s'ouvre
dans le navigateur, avec ce titre affiché. C'est tout le principe de
Streamlit : chaque ligne de code qui commence par `st.` ajoute un élément
visible sur la page.

---

## Partie 3 — Ajouter les questions, une par une

On ajoute maintenant les questions du formulaire. On commence par une
seule, pour voir comment ça marche :

```python
type_cheveux = st.radio(
    "Quel est ton type de cheveux ?",
    ["Lisses", "Ondulés", "Bouclés", "Crépus"],
)
```

`st.radio(...)` affiche une question avec plusieurs choix, dont un seul
peut être sélectionné. Le choix de la personne est automatiquement rangé
dans la variable `type_cheveux`. Relance l'application : tu vois la
question apparaître, et tu peux cliquer sur une réponse.

On répète ensuite le même principe pour les autres questions, avec
d'autres widgets Streamlit :

```python
soucis = st.multiselect(
    "Quels sont tes soucis actuels ?",
    ["Cheveux secs", "Casse", "Pousse lente", "Nœuds"],
)

pays = st.text_input("Dans quel pays habites-tu ?", value="Cameroun")
```

- `st.multiselect` : comme `st.radio`, mais on peut cocher plusieurs
  réponses à la fois. Le résultat est une **liste**.
- `st.text_input` : un champ de texte libre, sur une seule ligne.

À chaque fois qu'on ajoute une question, on relance l'application pour
vérifier qu'elle s'affiche bien, **avant** de passer à la suite. C'est une
bonne habitude : avancer petit pas par petit pas, et tester souvent.

---

## Partie 4 — Écrire sa première fonction

Maintenant qu'on a les réponses du formulaire, on veut construire une
phrase de recherche à envoyer à un moteur de recherche. Plutôt que d'écrire
ce calcul directement dans la page, on l'écrit dans une **fonction** : ça
rend le code plus lisible, et on peut le réutiliser facilement.

Voici d'abord une fonction toute simple, pour comprendre le principe :

```python
def dire_bonjour(prenom):
    message = "Bonjour " + prenom + " !"
    return message

print(dire_bonjour("Awa"))  # affiche : Bonjour Awa !
```

- `def dire_bonjour(prenom):` : on déclare une fonction nommée
  `dire_bonjour`, qui prend un ingrédient appelé `prenom`.
- `return message` : la fonction renvoie le résultat calculé, pour qu'on
  puisse s'en servir ailleurs dans le programme.

Avec ce même principe, on écrit maintenant notre vraie fonction, qui
transforme les réponses du formulaire en une phrase de recherche :

```python
def construire_la_requete_de_recherche(type_cheveux, soucis, etat_pointes, pays):
    mots_cles = []
    mots_cles.append(type_cheveux)
    for souci in soucis:
        mots_cles.append(souci)
    mots_cles.append(etat_pointes)

    requete = "meilleurs produits capillaires " + " ".join(mots_cles)
    requete += f" disponibles en {pays}, acheter en ligne"
    return requete
```

Ce qui est nouveau ici :

- `mots_cles = []` crée une liste vide, comme un panier.
- `mots_cles.append(...)` ajoute un élément dans ce panier.
- `for souci in soucis:` répète l'ajout pour chaque souci coché dans le
  formulaire (il peut y en avoir 0, 1, ou plusieurs).
- `" ".join(mots_cles)` recolle tous les éléments du panier en une seule
  phrase, séparés par des espaces.
- `f"... {pays} ..."` est une "f-string" : elle permet d'insérer la valeur
  d'une variable directement dans un texte.

Teste-la tout de suite, pour voir ce qu'elle donne :

```python
exemple = construire_la_requete_de_recherche("Bouclés", ["Cheveux secs", "Pellicules"], "Sèches", "Cameroun")
st.write(exemple)
```

---

## Partie 5 — Aller chercher de vrais résultats sur internet

On a notre phrase de recherche. Maintenant, on veut l'envoyer à un vrai
moteur de recherche. On utilise un service appelé **Tavily**, fait
spécialement pour donner des résultats web à une intelligence artificielle.

Pour l'utiliser, il faut une **clé API** : un mot de passe secret, propre à
ton compte, qui prouve que tu as le droit d'utiliser ce service. On ne doit
**jamais** écrire cette clé directement dans le code ; on la range dans un
fichier séparé nommé `.env`, et on la lit avec `os.getenv(...)`.

```python
load_dotenv()  # lit le fichier .env et rend les clés disponibles

def rechercher_des_produits_sur_internet(requete):
    cle_api_tavily = os.getenv("TAVILY_API_KEY")
    client_tavily = TavilyClient(api_key=cle_api_tavily)
    reponse = client_tavily.search(query=requete, max_results=8)
    return reponse["results"]
```

- `TavilyClient(api_key=...)` crée un "client" : un objet qui sait comment
  parler au service Tavily avec ta clé.
- `client_tavily.search(query=requete, max_results=8)` envoie la recherche
  et demande 8 résultats au maximum.
- `reponse["results"]` récupère, dans la réponse, uniquement la liste des
  résultats trouvés (chaque résultat contient un titre, un lien, un
  extrait de texte).

Teste cette fonction avant de continuer :

```python
resultats = rechercher_des_produits_sur_internet(exemple)
st.write(resultats)
```

Tu dois voir une liste de vraies pages web s'afficher.

---

## Partie 6 — Rassembler toutes les informations en un seul message

L'intelligence artificielle a besoin de tout savoir d'un coup : les
réponses du formulaire, **et** les résultats trouvés sur internet. On
écrit une fonction qui construit un seul grand texte avec tout ça :

```python
def construire_le_message_pour_lia(type_cheveux, soucis, etat_pointes, pays, resultats_de_recherche):
    message = f"Type de cheveux : {type_cheveux}\n"
    message += f"Soucis : {', '.join(soucis)}\n"
    message += f"Pointes : {etat_pointes}\n"
    message += f"Pays : {pays}\n\n"

    message += "Voici des résultats trouvés sur internet :\n"
    for resultat in resultats_de_recherche:
        message += f"- {resultat['title']} ({resultat['url']})\n"

    return message
```

Ici, on répète deux idées déjà vues : la **boucle `for`** pour parcourir
chaque résultat trouvé, et la **f-string** pour insérer les valeurs dans
le texte. `message +=` veut dire "ajoute ce texte à la suite de ce qu'il y
avait déjà dans `message`".

*(Dans le vrai fichier `app.py`, cette fonction prend un peu plus
d'informations — fréquence de lavage, précision libre — mais le principe
est exactement le même.)*

---

## Partie 7 — Parler à l'intelligence artificielle

Maintenant, on envoie ce message complet à l'IA, grâce au service **Groq**
(gratuit). On lui donne aussi un **prompt système** : des règles à
respecter, données une fois pour toutes, avant la question.

```python
PROMPT_SYSTEME = """Tu es un assistant spécialisé en soins capillaires.
Tu réponds toujours en français, avec des mots simples.
Tu ne recommandes que des produits présents dans les résultats fournis."""

def demander_a_groq(message_utilisateur):
    cle_api_groq = os.getenv("GROQ_API_KEY")
    client_groq = Groq(api_key=cle_api_groq)

    reponse = client_groq.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": PROMPT_SYSTEME},
            {"role": "user", "content": message_utilisateur},
        ],
    )
    return reponse.choices[0].message.content
```

- `messages=[...]` est une **liste** de deux éléments. Chaque élément est
  un petit paquet d'informations (on l'appelle un *dictionnaire*) avec un
  `"role"` (qui parle : le système, ou l'utilisateur) et un `"content"`
  (le texte).
- `client_groq.chat.completions.create(...)` envoie tout ça à l'IA et
  attend sa réponse.
- `reponse.choices[0].message.content` va chercher, dans la réponse
  renvoyée, uniquement le texte écrit par l'IA.

---

## Partie 8 — Relier le bouton à tout le reste

Il ne reste plus qu'à ajouter un bouton, et à appeler nos fonctions dans
l'ordre quand on clique dessus :

```python
if st.button("Analyser mes cheveux"):
    requete = construire_la_requete_de_recherche(type_cheveux, soucis, etat_pointes, pays)
    resultats = rechercher_des_produits_sur_internet(requete)
    message = construire_le_message_pour_lia(type_cheveux, soucis, etat_pointes, pays, resultats)
    reponse_de_lia = demander_a_groq(message)
    st.markdown(reponse_de_lia)
```

- `if st.button("..."):` : le code à l'intérieur ne s'exécute que quand la
  personne clique sur le bouton.
- Ensuite, on appelle nos quatre fonctions **dans l'ordre**, chacune
  utilisant le résultat de la précédente.
- `st.markdown(...)` affiche le texte final en le mettant en forme
  automatiquement (titres, listes, liens cliquables...).

Dans le vrai `app.py`, tout ce bloc est entouré d'un `try / except`, pour
afficher un message d'erreur propre si quelque chose se passe mal (pas
d'internet, clé API invalide...) plutôt que de faire planter la page. C'est
une sécurité en plus, pas une nouvelle idée : on a juste encadré ce même
bloc de code.

---

## Pour aller plus loin

Maintenant que tu as reconstruit la logique étape par étape, ouvre le
vrai fichier `app.py` à côté de ce document : tu devrais reconnaître
**chacune** des fonctions que tu viens d'écrire ici, juste un peu plus
complètes (plus de questions dans le formulaire, plus de champs dans les
messages, une gestion des erreurs). Essaie de les expliquer à voix haute,
comme si tu donnais ce même petit cours à quelqu'un d'autre : c'est la
meilleure façon de vérifier que tu as bien compris.
