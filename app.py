"""
Agent IA de diagnostic capillaire.
Une page Streamlit pose des questions sur les cheveux, puis une IA (Groq)
propose un diagnostic et des produits réels trouvés sur internet (Tavily).
"""

import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

# On charge les variables secrètes (les clés API) depuis le fichier .env.
# Ainsi, les clés ne sont jamais écrites directement dans ce fichier.
load_dotenv()


def obtenir_une_cle_api(nom_de_la_cle):
    """Trouve une clé API, qu'elle vienne du fichier .env (en local sur ton
    ordinateur) ou des "secrets" configurés sur Streamlit Cloud (une fois
    l'application mise en ligne). On cherche d'abord dans le fichier .env,
    et si elle n'y est pas, on cherche dans les secrets de Streamlit Cloud.
    """
    valeur = os.getenv(nom_de_la_cle)
    if valeur:
        return valeur
    try:
        return st.secrets[nom_de_la_cle]
    except Exception:
        return None

# Le modèle d'IA de Groq que l'on utilise pour écrire le diagnostic.
# Il est gratuit (dans la limite d'un certain nombre de messages par jour).
MODELE_GROQ = "openai/gpt-oss-120b"

# Ces instructions sont envoyées à l'IA avant chaque question.
# Elles définissent les règles que l'IA doit toujours respecter.
PROMPT_SYSTEME = """Tu es un assistant spécialisé en soins capillaires, qui s'adresse à un public francophone.

RÈGLES À RESPECTER ABSOLUMENT :
1. Tu ne poses jamais de diagnostic médical. Si la personne a signalé une chute de
   cheveux importante ou des plaques/rougeurs sur le cuir chevelu, tu commences
   OBLIGATOIREMENT ta réponse par un conseil de consulter un dermatologue ou un médecin.
2. Tu ne recommandes QUE des produits qui apparaissent dans les résultats de recherche
   internet fournis dans le message de l'utilisateur, avec leur lien exact.
   Tu n'inventes jamais un produit, une marque, un prix ou un lien qui ne serait pas
   présent dans ces résultats de recherche.
3. Tu réponds toujours en français, avec des mots simples et bienveillants.

FORMAT DE LA RÉPONSE (en Markdown) :
- Un court diagnostic (quelques phrases).
- Une liste de 3 à 5 produits recommandés, chacun avec : nom, marque, raison du choix,
  prix indicatif si disponible, et le lien trouvé.
- Une routine simple, étape par étape.
"""


def construire_la_requete_de_recherche(type_cheveux, soucis, etat_pointes, pays):
    """Fabrique une courte phrase à envoyer à Tavily pour chercher des produits.

    On assemble les mots-clés les plus importants du formulaire : le type de
    cheveux, les soucis principaux et le pays, pour que la recherche sur
    internet trouve des produits adaptés et disponibles dans ce pays.
    """
    mots_cles = []
    mots_cles.append(type_cheveux)
    for souci in soucis:
        mots_cles.append(souci)
    mots_cles.append(etat_pointes)

    requete = "meilleurs produits capillaires " + " ".join(mots_cles)
    requete += f" disponibles en {pays}, acheter en ligne"
    return requete


def rechercher_des_produits_sur_internet(requete):
    """Appelle Tavily pour obtenir de vrais résultats de recherche sur le web.

    Tavily renvoie une liste de pages web trouvées (titre, lien, extrait de
    texte). C'est cette liste qui sera ensuite donnée à l'IA, pour qu'elle ne
    puisse parler que de produits qui existent vraiment.
    """
    cle_api_tavily = obtenir_une_cle_api("TAVILY_API_KEY")
    client_tavily = TavilyClient(api_key=cle_api_tavily)
    reponse = client_tavily.search(query=requete, max_results=8)
    return reponse["results"]


def construire_le_message_pour_lia(
    type_cheveux,
    soucis,
    etat_pointes,
    frequence_lavage,
    pays,
    autre_chose,
    resultats_de_recherche,
):
    """Rassemble les réponses du formulaire et les résultats de recherche
    en un seul texte clair, qui sera envoyé à l'IA.
    """
    if soucis:
        texte_des_soucis = ", ".join(soucis)
    else:
        texte_des_soucis = "aucun souci particulier"

    message = "Voici la situation d'une personne qui souhaite des conseils capillaires :\n"
    message += f"- Type de cheveux : {type_cheveux}\n"
    message += f"- Soucis signalés : {texte_des_soucis}\n"
    message += f"- État des pointes : {etat_pointes}\n"
    message += f"- Fréquence de lavage : {frequence_lavage}\n"
    message += f"- Pays (pour trouver des produits disponibles) : {pays}\n"
    if autre_chose:
        message += f"- Précision supplémentaire donnée par la personne : {autre_chose}\n"

    message += "\nVoici des résultats de recherche trouvés sur internet, à utiliser "
    message += "pour recommander des produits réels (ne cite que ce qui est ici) :\n"
    for resultat in resultats_de_recherche:
        message += f"- Titre : {resultat['title']}\n"
        message += f"  Lien : {resultat['url']}\n"
        message += f"  Extrait : {resultat['content']}\n"

    return message


def demander_a_groq(message_utilisateur):
    """Envoie le message à l'IA Groq et renvoie sa réponse en texte (Markdown)."""
    cle_api_groq = obtenir_une_cle_api("GROQ_API_KEY")
    client_groq = Groq(api_key=cle_api_groq)

    reponse = client_groq.chat.completions.create(
        model=MODELE_GROQ,
        messages=[
            {"role": "system", "content": PROMPT_SYSTEME},
            {"role": "user", "content": message_utilisateur},
        ],
    )
    return reponse.choices[0].message.content


# ----------------------------------------------------------------------------
# À partir d'ici commence la page Streamlit : c'est ce que voit la personne
# qui utilise l'application dans son navigateur.
# ----------------------------------------------------------------------------

st.title("Agent IA de diagnostic capillaire")
st.write(
    "Réponds aux questions ci-dessous, puis clique sur le bouton pour recevoir "
    "un diagnostic et des produits recommandés."
)

# Question 1 : le type de cheveux (une seule réponse possible).
type_cheveux = st.radio(
    "Quel est ton type de cheveux ?",
    ["Lisses", "Ondulés", "Bouclés", "Crépus"],
)

# Question 2 : les soucis actuels (plusieurs réponses possibles).
soucis = st.multiselect(
    "Quels sont tes soucis actuels ? (plusieurs choix possibles)",
    [
        "Cheveux secs",
        "Casse",
        "Pousse lente",
        "Nœuds",
        "Cuir chevelu qui gratte",
        "Pellicules",
        "Cuir chevelu gras",
        "Chute importante",
        "Plaques ou rougeurs",
    ],
)

# Question 3 : l'état des pointes (une seule réponse possible).
etat_pointes = st.radio(
    "Dans quel état sont tes pointes ?",
    ["En bon état", "Sèches", "Fourchues"],
)

# Question 4 : la fréquence de lavage (une seule réponse possible).
frequence_lavage = st.radio(
    "À quelle fréquence laves-tu tes cheveux ?",
    ["Plusieurs fois par semaine", "1 fois par semaine", "Moins souvent"],
)

# Question 5 : le pays, pour trouver des produits disponibles sur place.
pays = st.text_input("Dans quel pays habites-tu ?", value="Cameroun")

# Question 6 : un champ libre pour préciser quelque chose en plus.
autre_chose = st.text_area("Autre chose à préciser ? (facultatif)")

# Le bouton qui déclenche l'analyse.
if st.button("Analyser mes cheveux"):
    # On vérifie d'abord que les deux clés API sont bien présentes.
    if not obtenir_une_cle_api("GROQ_API_KEY") or not obtenir_une_cle_api("TAVILY_API_KEY"):
        st.error(
            "Clé API manquante. Vérifie que le fichier .env contient bien "
            "GROQ_API_KEY et TAVILY_API_KEY."
        )
    else:
        try:
            with st.spinner("Recherche de produits sur internet..."):
                requete = construire_la_requete_de_recherche(
                    type_cheveux, soucis, etat_pointes, pays
                )
                resultats_de_recherche = rechercher_des_produits_sur_internet(requete)

            with st.spinner("L'IA rédige ton diagnostic..."):
                message_pour_lia = construire_le_message_pour_lia(
                    type_cheveux,
                    soucis,
                    etat_pointes,
                    frequence_lavage,
                    pays,
                    autre_chose,
                    resultats_de_recherche,
                )
                reponse_de_lia = demander_a_groq(message_pour_lia)

            st.markdown(reponse_de_lia)

        except Exception as erreur:
            st.error(
                "Une erreur est survenue pendant l'analyse. "
                "Vérifie ta connexion internet et tes clés API.\n\n"
                f"Détail technique : {erreur}"
            )
