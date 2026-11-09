# Préparation à la soutenance — Agent IA de diagnostic capillaire

## 1. Le projet en 5 lignes

Cette application pose des questions sur l'état de ses cheveux à la personne
qui l'utilise (type de cheveux, soucis, pointes, fréquence de lavage, pays).
Elle cherche ensuite de vrais produits en vente sur internet, adaptés à ces
réponses. Une intelligence artificielle lit ces réponses et ces produits,
puis rédige un diagnostic simple, une liste de produits recommandés avec
leurs liens, et une routine de soin étape par étape. Tout s'affiche sur une
seule page web, créée avec Streamlit.

## 2. Schéma du fonctionnement

```
 ┌──────────────────┐
 │   Questionnaire   │   La personne répond aux questions
 │   (page web)      │   sur ses cheveux.
 └─────────┬─────────┘
           │ clic sur "Analyser mes cheveux"
           ▼
 ┌──────────────────┐
 │  Recherche web    │   On envoie une phrase de recherche
 │   (Tavily)        │   à Tavily, qui renvoie de vraies pages
 └─────────┬─────────┘   web (produits réels, avec leurs liens).
           │
           ▼
 ┌──────────────────┐
 │   Intelligence    │   On envoie à l'IA : les réponses du
 │ artificielle (Groq)│   formulaire + les résultats de Tavily.
 └─────────┬─────────┘   L'IA rédige la réponse.
           │
           ▼
 ┌──────────────────┐
 │  Résultat affiché │   Diagnostic, produits recommandés,
 │   (page web)       │   routine, en Markdown.
 └──────────────────┘
```

## 3. Explication de app.py, bloc par bloc

### Bloc des imports

```python
import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient
```

`import` permet d'utiliser des bibliothèques, c'est-à-dire du code déjà écrit
par d'autres personnes, pour ne pas tout réécrire soi-même. `os` sert à lire
les clés API. `streamlit` sert à construire la page web. `dotenv` sert à lire
le fichier `.env`. `groq` et `tavily` sont les bibliothèques officielles pour
parler à l'IA Groq et au moteur de recherche Tavily.

### Chargement des clés API

```python
load_dotenv()
```

Cette ligne lit le fichier `.env` et rend les clés API disponibles dans le
programme, sans jamais les écrire en clair dans le code.

### Le modèle d'IA et le prompt système

```python
MODELE_GROQ = "llama-3.3-70b-versatile"

PROMPT_SYSTEME = """Tu es un assistant spécialisé en soins capillaires...
"""
```

`MODELE_GROQ` est le nom de l'intelligence artificielle utilisée.
`PROMPT_SYSTEME` est un texte d'instructions donné à l'IA avant chaque
question : il lui impose ses règles (ne jamais faire de diagnostic médical
dans certains cas, ne jamais inventer de produit, répondre en français).

### Fonction 1 : construire_la_requete_de_recherche

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

Cette fonction prend les réponses du formulaire et construit une phrase de
recherche, par exemple *"meilleurs produits capillaires Bouclés Cheveux secs
Sèches disponibles en Cameroun, acheter en ligne"*. C'est cette phrase qui
sera envoyée au moteur de recherche.

### Fonction 2 : rechercher_des_produits_sur_internet

```python
def rechercher_des_produits_sur_internet(requete):
    cle_api_tavily = os.getenv("TAVILY_API_KEY")
    client_tavily = TavilyClient(api_key=cle_api_tavily)
    reponse = client_tavily.search(query=requete, max_results=8)
    return reponse["results"]
```

Cette fonction envoie la phrase de recherche à Tavily, qui cherche
réellement sur internet et renvoie jusqu'à 8 résultats (des pages web avec
un titre, un lien et un court extrait). C'est cette étape qui garantit que
les produits proposés existent vraiment.

### Fonction 3 : construire_le_message_pour_lia

```python
def construire_le_message_pour_lia(..., resultats_de_recherche):
    ...
    for resultat in resultats_de_recherche:
        message += f"- Titre : {resultat['title']}\n"
        message += f"  Lien : {resultat['url']}\n"
        message += f"  Extrait : {resultat['content']}\n"
    return message
```

Cette fonction rassemble tout ce que l'IA doit savoir dans un seul texte :
les réponses du formulaire, et la liste des résultats trouvés par Tavily.
C'est ce texte complet qui sera envoyé à l'IA.

### Fonction 4 : demander_a_groq

```python
def demander_a_groq(message_utilisateur):
    cle_api_groq = os.getenv("GROQ_API_KEY")
    client_groq = Groq(api_key=cle_api_groq)

    reponse = client_groq.chat.completions.create(
        model=MODELE_GROQ,
        messages=[
            {"role": "system", "content": PROMPT_SYSTEME},
            {"role": "user", "content": message_utilisateur},
        ],
    )
    return reponse.choices[0].message.content
```

Cette fonction envoie le texte complet à l'IA Groq, avec le prompt système
en premier (les règles) et le message préparé juste après (les informations).
L'IA renvoie sa réponse, et on en extrait uniquement le texte.

### Le formulaire (questions à l'écran)

```python
type_cheveux = st.radio("Quel est ton type de cheveux ?", [...])
soucis = st.multiselect("Quels sont tes soucis actuels ?", [...])
```

`st.radio` affiche des boutons où on ne peut choisir qu'une seule réponse.
`st.multiselect` affiche une liste où on peut cocher plusieurs réponses.
`st.text_input` et `st.text_area` affichent des champs de texte libre.

### Le bouton et le déroulement final

```python
if st.button("Analyser mes cheveux"):
    if not os.getenv("GROQ_API_KEY") or not os.getenv("TAVILY_API_KEY"):
        st.error("Clé API manquante...")
    else:
        try:
            requete = construire_la_requete_de_recherche(...)
            resultats_de_recherche = rechercher_des_produits_sur_internet(requete)
            message_pour_lia = construire_le_message_pour_lia(...)
            reponse_de_lia = demander_a_groq(message_pour_lia)
            st.markdown(reponse_de_lia)
        except Exception as erreur:
            st.error("Une erreur est survenue...")
```

Quand on clique sur le bouton, le programme vérifie d'abord que les clés
API sont présentes. Ensuite, il appelle les quatre fonctions dans l'ordre :
construire la recherche, chercher sur internet, construire le message,
demander à l'IA. Le `try/except` sert de filet de sécurité : si une erreur
survient (pas internet, clé API invalide...), un message clair s'affiche au
lieu de faire planter l'application.

## 4. Glossaire

- **API (Application Programming Interface)** : une façon pour un programme
  de demander un service à un autre programme sur internet (ici, demander à
  Groq de réfléchir, ou à Tavily de chercher).
- **Clé API** : un mot de passe secret qui prouve qu'on a le droit d'utiliser
  une API, et qui permet de compter l'utilisation qu'on en fait.
- **Streamlit** : une bibliothèque Python qui permet de créer une page web
  interactive sans connaître le développement web classique (HTML, CSS...).
- **Prompt** : le texte qu'on envoie à une intelligence artificielle pour lui
  demander quelque chose.
- **Prompt système** : un prompt spécial, envoyé avant la question de
  l'utilisateur, qui donne des règles générales que l'IA doit toujours
  suivre.
- **Modèle d'IA** : le programme d'intelligence artificielle précis qui va
  lire le prompt et générer une réponse (ici, `openai/gpt-oss-120b`,
  fourni gratuitement par Groq).
- **Recherche web** : le fait de chercher automatiquement des informations
  sur internet, ici grâce à Tavily, plutôt que d'inventer des réponses.
- **Variable d'environnement** : une information (comme une clé API) stockée
  en dehors du code, dans un fichier séparé (`.env`), pour ne pas l'écrire en
  clair dans le programme.
- **Bibliothèque** : un ensemble de code déjà écrit par d'autres personnes,
  qu'on peut réutiliser dans son propre programme avec `import`.

## 5. Limites du projet et améliorations possibles

**Limites actuelles :**
- Le diagnostic n'est pas un avis médical, seulement une aide générale.
- La qualité des produits proposés dépend de ce que Tavily trouve au moment
  de la recherche : certains pays ou produits très spécifiques peuvent
  donner peu de résultats.
- L'IA peut parfois mal interpréter un résultat de recherche, même si le
  prompt système lui interdit d'inventer des produits.
- Il n'y a pas d'historique : à chaque analyse, tout est recalculé depuis le
  début.

**Améliorations possibles :**
- Sauvegarder les analyses précédentes pour pouvoir les consulter plus tard.
- Permettre de choisir plusieurs pays ou plusieurs langues.
- Ajouter des photos ou un moyen d'uploader une photo des cheveux pour
  affiner le diagnostic.
- Comparer les prix de plusieurs sites pour un même produit.

## 6. 10 questions que le jury pourrait poser

1. **Pourquoi avoir utilisé Groq plutôt que Claude ou ChatGPT ?**
   Groq propose un accès gratuit à son IA, ce qui permet d'utiliser
   l'application sans frais, contrairement à d'autres services payants.

2. **Comment l'application trouve-t-elle de vrais produits, et pas des
   produits inventés ?**
   Elle utilise Tavily, un service de recherche web, pour trouver de vraies
   pages internet. Ces résultats sont ensuite donnés à l'IA, à qui on
   interdit (dans le prompt système) de parler d'autre chose que de ce
   qu'elle a reçu.

3. **Qu'est-ce qu'un prompt système, et pourquoi est-il séparé dans le
   code ?**
   C'est le texte de règles donné à l'IA avant chaque question. Il est placé
   dans une variable bien visible en haut du fichier pour qu'on puisse le
   lire, le montrer et le modifier facilement, sans devoir fouiller dans le
   reste du code.

4. **Que se passe-t-il si la clé API est fausse ou absente ?**
   Le programme vérifie la présence des clés avant d'appeler les services.
   S'il manque une clé, ou si un appel échoue, un message d'erreur clair en
   français s'affiche, au lieu de faire planter l'application.

5. **Pourquoi la clé API n'est-elle pas écrite directement dans le code ?**
   Pour des raisons de sécurité : si le code est partagé ou mis en ligne
   (par exemple sur GitHub), la clé secrète ne doit jamais être visible.
   Elle est donc placée dans un fichier séparé, `.env`, qui n'est jamais
   partagé (grâce au fichier `.gitignore`).

6. **Comment l'application empêche-t-elle de donner un diagnostic
   médical dangereux ?**
   Le prompt système oblige l'IA à toujours conseiller de consulter un
   dermatologue ou un médecin dès que la personne signale une chute de
   cheveux importante ou des plaques/rougeurs.

7. **Pourquoi avoir choisi Streamlit pour l'interface ?**
   Streamlit permet de créer une page web interactive uniquement avec du
   code Python, sans avoir besoin d'apprendre le développement web
   classique (HTML, CSS, JavaScript).

8. **Que fait la fonction `construire_le_message_pour_lia` exactement ?**
   Elle rassemble en un seul texte toutes les réponses du formulaire et les
   résultats trouvés sur internet, pour que l'IA ait toutes les
   informations nécessaires en une seule fois.

9. **L'application fonctionne-t-elle sans connexion internet ?**
   Non. Elle a besoin d'internet pour contacter Tavily (la recherche) et
   Groq (l'IA). Sans connexion, une erreur s'affiche.

10. **Quelles sont les limites principales du projet aujourd'hui ?**
    Ce n'est pas un avis médical, la qualité des produits trouvés dépend de
    ce que la recherche web renvoie sur le moment, et il n'y a pas
    d'historique des analyses précédentes.
