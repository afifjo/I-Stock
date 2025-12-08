
# 🚀 Guide de Déploiement sur Render.com

Ce guide vous explique comment mettre en ligne votre application **I-NVENTORY** gratuitement (ou à faible coût) sur Render.

---

## ⚠️ Important : Base de Données
Par défaut, votre application utilise **SQLite** (un fichier local).
Sur Render (et la plupart des clouds), le disque dur est **éphémère**. Cela signifie que si vous redémarrez l'application, **toutes les données (utilisateurs, stock) seront effacées**.

👉 **Solution Recommandée** : Ajouter une base de données **PostgreSQL** gratuite sur Render. (Expliqué ci-dessous).

---

## Étape 1 : Mettre le code sur GitHub
(Si ce n'est pas déjà fait)
1.  Créez un compte sur [GitHub.com](https://github.com).
2.  Créez un nouveau "Repository" (Dépôt) nommé `inventory-app`.
3.  Envoyez votre code actuel vers ce dépôt.

## Étape 2 : Créer le service Web sur Render
1.  Créez un compte sur [Render.com](https://render.com).
2.  Cliquez sur **"New"** > **"Web Service"**.
3.  Connectez votre compte GitHub et sélectionnez le dépôt `inventory-app`.

### Configuration
*   **Name** : `i-watch-inventory` (ou autre)
*   **Region** : Frankfurt (EU Central) - Plus proche de la Tunisie.
*   **Branch** : `main`
*   **Runtime** : `Python 3`
*   **Build Command** : `pip install -r requirements.txt`
*   **Start Command** : `gunicorn wsgi:app`
*   **Instance Type** : `Free`

## Étape 3 : Variables d'Environnement
Dans la section "Environment Variables", ajoutez :

| Key | Value |
| :--- | :--- |
| `PYTHON_VERSION` | `3.10.12` (ou 3.11.0) |
| `SECRET_KEY` | (Générez une longue phrase aléatoire) |
| `MAIL_USERNAME` | `afifjouili9@gmail.com` |
| `MAIL_PASSWORD` | `Papa22030671` (ou votre App Password si besoin) |

## Étape 4 : Ajouter la Base de Données (PostgreSQL)
1.  Dans le menu Render, cliquez sur **"New"** > **"PostgreSQL"**.
2.  Nom : `inventory-db`
3.  Database : `inventory`
4.  User : `user`
5.  Region : **Même région que le Web Service** (ex: Frankfurt).
6.  Instance Type : `Free`.
7.  Cliquez sur **Create Database**.

Une fois créée, copiez l'**Internal Database URL** (qui ressemble à `postgres://user:pass@host...`).

8.  Retournez dans votre **Web Service** > **Environment**.
9.  Ajoutez une nouvelle variable :
    *   **Key** : `DATABASE_URL`
    *   **Value** : (Collez l'URL copié juste avant)

## Étape 5 : Déployer
Render détectera les changements et déploiera automatiquement.
Une fois terminé, vous aurez une URL du type `https://i-watch-inventory.onrender.com`.

L'application est prête et vos données seront sauvegardées grâce à PostgreSQL ! 🚀
