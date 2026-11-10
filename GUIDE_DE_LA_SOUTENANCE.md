# Guide pratique pour le jour de la soutenance

Ce document n'explique pas le code. Il explique **quoi faire concrètement**,
étape par étape, pour présenter l'application devant le jury sans stress,
même sans aucune connaissance en programmation.

**Lien de l'application à utiliser le jour de la soutenance :**

➡️ **https://agent-ia-diagnostic-capillaire.streamlit.app/**

Garde ce lien aussi dans tes favoris et/ou dans un SMS/note sur ton
téléphone, au cas où.

---

## 1. À faire AVANT le jour J (une seule fois, quelques jours avant)

- [ ] Ouvre le lien de l'application dans un navigateur et vérifie qu'elle
      s'affiche bien.
- [ ] Fais un test complet : remplis le formulaire, clique sur
      "Analyser mes cheveux", et vérifie qu'un résultat s'affiche bien
      (diagnostic + produits + routine).
- [ ] **Important :** si l'application n'a pas été utilisée depuis plusieurs
      jours, elle "s'endort" automatiquement (c'est normal, pour économiser
      les ressources). La première personne qui ouvre le lien doit parfois
      patienter 30 secondes à 1 minute, le temps qu'elle se "réveille", avec
      un message à l'écran du type "This app has gone to sleep". **Fais donc
      un test la veille ou quelques heures avant ta soutenance**, pour que
      l'application soit déjà "réveillée" le jour J.
- [ ] Prends une ou deux captures d'écran d'une analyse complète réussie
      (diagnostic + produits + routine affichés). Garde-les sur ton
      téléphone ou ton ordinateur, dans le dossier du projet par exemple.
      C'est ton **plan B** si jamais internet ne fonctionne pas le jour J.
- [ ] Relis le document `EXPLICATION_SOUTENANCE.md` une fois en entier,
      surtout la partie 1 ("le projet en 5 lignes") et la partie 6
      (questions du jury).

## 2. Le jour de la soutenance, juste avant de commencer

1. Ouvre le navigateur et affiche le lien de l'application **avant** de
   commencer à parler, pour qu'elle soit déjà chargée quand tu en auras
   besoin.
2. Vérifie que tu es bien connectée au wifi de la salle.
3. Laisse la page ouverte dans un onglet, et garde aussi tes captures
   d'écran de secours ouvertes dans un autre onglet ou une autre fenêtre.

## 3. Pendant la présentation : le déroulé pas à pas

### Étape 1 — Tu expliques le projet en mots simples (30 secondes)

Tu peux dire quelque chose comme :

> "J'ai créé une petite application qui aide une personne à savoir quels
> produits capillaires acheter. La personne répond à quelques questions
> sur ses cheveux, l'application va chercher de vrais produits en vente sur
> internet, puis une intelligence artificielle rédige un diagnostic et une
> routine de soin adaptée."

### Étape 2 — Tu montres le formulaire à l'écran

Remplis les champs devant le jury, par exemple avec cet exemple (tu peux
choisir un autre exemple si tu préfères, du moment qu'il est réaliste) :

- Type de cheveux : **Bouclés**
- Soucis : **Cheveux secs** et **Pellicules**
- État des pointes : **Sèches**
- Fréquence de lavage : **1 fois par semaine**
- Pays : **Cameroun**
- Autre chose à préciser : *(tu peux laisser vide)*

### Étape 3 — Tu cliques sur "Analyser mes cheveux"

Pendant que ça charge (quelques secondes), tu peux expliquer ce qui se
passe "dans les coulisses", sans parler de code :

> "Là, l'application est en train de chercher de vrais produits sur
> internet qui correspondent à ces réponses. Ensuite, elle envoie ces
> informations à une intelligence artificielle, qui rédige la réponse
> finale."

### Étape 4 — Tu montres le résultat au jury

Quand la réponse s'affiche, montre au jury les trois parties, en les
nommant clairement :

1. **Le diagnostic** : un petit résumé de la situation des cheveux.
2. **Les produits recommandés** : une liste de 3 à 5 produits réels, avec
   leur marque, la raison du choix, et un lien vers où les trouver.
3. **La routine** : les étapes à suivre, dans l'ordre.

## 4. Si le jury pose une question

- Pour une question sur **le fonctionnement général** ou **pourquoi tel
  choix a été fait** : la réponse est probablement déjà écrite dans
  `EXPLICATION_SOUTENANCE.md`, section 6 ("10 questions que le jury
  pourrait poser"). Relis cette section avant le jour J pour la connaître
  par cœur.
- Pour une question sur **une ligne de code précise** : le document
  `EXPLICATION_SOUTENANCE.md`, section 3, explique chaque bloc du fichier
  `app.py` en français simple. Tu peux t'y référer si besoin.
- Si tu ne sais vraiment pas répondre : il vaut toujours mieux dire
  calmement "Je ne suis pas sûre, je préfère vérifier plutôt que de vous
  donner une mauvaise information" plutôt que d'improviser une réponse
  fausse.

## 5. Plan B : si internet ne fonctionne pas le jour J

Ça n'annule pas ta présentation ! Tu peux dire :

> "Je vais vous montrer un exemple de résultat que l'application a généré,
> puisque je n'ai pas de connexion internet stable ici."

Et montrer les captures d'écran préparées à l'étape 1. L'important est de
pouvoir quand même expliquer le fonctionnement et montrer à quoi ressemble
un résultat.
