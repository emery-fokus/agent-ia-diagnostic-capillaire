"""
Agent IA de diagnostic capillaire.
Une page Streamlit pose des questions sur les cheveux, puis une IA (Groq)
propose un diagnostic et des produits réels trouvés sur internet (Tavily).
"""

import base64
import os

import streamlit as st
from dotenv import load_dotenv
from google import genai
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

# Le modèle d'IA de Google Gemini que l'on utilise pour regarder les photos.
# Il est gratuit aussi, et sait analyser des images (contrairement à Groq).
MODELE_GEMINI = "gemini-3.6-flash"

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
4. Si le message contient une "fiche décrivant ce qui est visible sur les photos",
   utilise-la pour enrichir ton diagnostic. Rappelle que les informations qui ne se
   voient pas sur une photo (comme la porosité) restent des estimations.

FORMAT DE LA RÉPONSE (en Markdown) :
- Un court diagnostic (quelques phrases).
- Une liste de 3 à 5 produits recommandés, chacun avec : nom, marque, raison du choix,
  prix indicatif si disponible, et le lien trouvé.
- Une routine simple, étape par étape.
"""

# Ces instructions sont envoyées à l'IA Gemini avant qu'elle ne regarde les photos.
PROMPT_SYSTEME_PHOTOS = """Tu regardes des photos de cheveux envoyées par une personne.

RÈGLES À RESPECTER ABSOLUMENT :
1. Tu ne poses jamais de diagnostic médical.
2. Tu décris uniquement ce que tu vois vraiment sur les photos (type de boucle,
   densité apparente, état des pointes, aspect du cuir chevelu). Tu n'inventes rien
   que tu ne peux pas voir sur les photos.
3. La porosité et l'élasticité ne se voient pas sur une photo : base-toi uniquement
   sur ce que la personne a déclaré, et précise bien que ce sont des "estimations
   déclarées par la personne", pas des observations que tu as faites toi-même.
4. Réponds en français, avec des mots simples, sous forme d'une courte fiche
   (quelques lignes). Ne propose pas de produits ici, ce n'est pas ton rôle.
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


def convertir_une_photo_en_base64(photo):
    """Transforme une photo prise par la personne en un format que l'on
    peut envoyer à l'IA Gemini : du texte encodé en base64, avec son type
    (JPEG, PNG...). C'est la façon dont Gemini attend de recevoir une image.
    """
    contenu = photo.getvalue()
    texte_encode = base64.b64encode(contenu).decode("utf-8")
    return {"type": "image", "data": texte_encode, "mime_type": photo.type}


def analyser_les_photos_avec_gemini(photos, cheveux_sechent_vite, meche_revient_en_place):
    """Envoie les photos des cheveux à l'IA Gemini, avec les deux informations
    que l'on ne peut pas voir sur une photo (porosité et élasticité), et
    renvoie une petite fiche décrivant ce qui est visible.
    """
    cle_api_gemini = obtenir_une_cle_api("GEMINI_API_KEY")
    client_gemini = genai.Client(api_key=cle_api_gemini)

    texte_de_la_demande = "Voici des photos de cheveux. Décris ce que tu observes.\n"
    texte_de_la_demande += f"La personne dit que ses cheveux sèchent vite après le lavage : {cheveux_sechent_vite}\n"
    texte_de_la_demande += f"La personne dit qu'une mèche mouillée étirée revient en place : {meche_revient_en_place}\n"

    contenu_envoye = []
    contenu_envoye.append({"type": "text", "text": texte_de_la_demande})
    for photo in photos:
        contenu_envoye.append(convertir_une_photo_en_base64(photo))

    reponse = client_gemini.interactions.create(
        model=MODELE_GEMINI,
        system_instruction=PROMPT_SYSTEME_PHOTOS,
        input=contenu_envoye,
    )
    return reponse.output_text


def construire_le_message_pour_lia(
    type_cheveux,
    soucis,
    etat_pointes,
    frequence_lavage,
    pays,
    autre_chose,
    resultats_de_recherche,
    fiche_profil_photos,
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

    if fiche_profil_photos:
        message += "\nVoici une fiche décrivant ce qui est visible sur les photos "
        message += "envoyées par la personne :\n"
        message += fiche_profil_photos + "\n"

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

# Questions 7 (facultatives) : des photos prises en direct pour affiner le
# diagnostic. st.camera_input ouvre vraiment la caméra dans le navigateur.
# Totalement facultatives : l'application fonctionne très bien sans elles,
# juste avec le questionnaire ci-dessus.
st.subheader("Photos (facultatif, pour un diagnostic plus précis)")
photo_profil = st.camera_input("Étape 1 : tourne la tête et montre tes cheveux de profil")
photo_pointes = st.camera_input("Étape 2 : montre tes pointes de près")
photo_meche = st.camera_input("Étape 3 : étire une mèche de cheveux et prends-la en photo")
photo_cuir_chevelu = st.camera_input("Étape 4 : montre ton cuir chevelu, en écartant tes cheveux")

# On rassemble les photos prises dans une liste (certaines peuvent être vides).
photos = []
if photo_profil is not None:
    photos.append(photo_profil)
if photo_pointes is not None:
    photos.append(photo_pointes)
if photo_meche is not None:
    photos.append(photo_meche)
if photo_cuir_chevelu is not None:
    photos.append(photo_cuir_chevelu)

# Ces deux informations ne se voient pas sur une photo, on les demande donc
# directement à la personne.
cheveux_sechent_vite = st.radio(
    "Tes cheveux sèchent-ils vite après le lavage ?",
    ["Oui", "Non", "Je ne sais pas"],
)
meche_revient_en_place = st.radio(
    "Si tu étires une mèche mouillée, revient-elle en place ?",
    ["Oui", "Non", "Je ne sais pas"],
)

# Le bouton qui déclenche l'analyse.
if st.button("Analyser mes cheveux"):
    # On vérifie d'abord que les clés API nécessaires sont bien présentes.
    cles_de_base_absentes = not obtenir_une_cle_api("GROQ_API_KEY") or not obtenir_une_cle_api("TAVILY_API_KEY")
    photos_envoyees = len(photos) > 0
    cle_gemini_absente = photos_envoyees and not obtenir_une_cle_api("GEMINI_API_KEY")

    if cles_de_base_absentes:
        st.error(
            "Clé API manquante. Vérifie que le fichier .env contient bien "
            "GROQ_API_KEY et TAVILY_API_KEY."
        )
    elif cle_gemini_absente:
        st.error(
            "Tu as pris des photos, mais la clé GEMINI_API_KEY est absente. "
            "Ajoute-la dans le fichier .env, ou enlève les photos pour continuer "
            "sans elles."
        )
    else:
        try:
            fiche_profil_photos = ""
            if photos_envoyees:
                with st.spinner("Analyse des photos..."):
                    fiche_profil_photos = analyser_les_photos_avec_gemini(
                        photos, cheveux_sechent_vite, meche_revient_en_place
                    )

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
                    fiche_profil_photos,
                )
                reponse_de_lia = demander_a_groq(message_pour_lia)

            st.markdown(reponse_de_lia)

        except Exception as erreur:
            st.error(
                "Une erreur est survenue pendant l'analyse. "
                "Vérifie ta connexion internet et tes clés API.\n\n"
                f"Détail technique : {erreur}"
            )
