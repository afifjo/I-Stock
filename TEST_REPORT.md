
# Plan de Tests & Rapport d'Exécution - I-NVENTORY

## 1. Stratégie de Test Globale
L'objectif est de garantir la stabilité, la sécurité et la fonctionnalité de l'application de gestion d'inventaire.
Approche : **Pyramide de tests** (plus de tests unitaires/intégration, quelques tests E2E critiques).

### Types de Tests
*   **Tests Unitaires** : Validation des modèles de données (User, Item, Staff) et règles métier.
*   **Tests d'Intégration** : Validation des routes, de l'authentification et des flux de données.
*   **Tests End-to-End (Simulés)** : Simulation d'un parcours utilisateur complet (Inscription -> Action -> Vérification -> Déconnexion).
*   **Tests de Sécurité** : Vérification des contrôles d'accès et headers (analyse).

## 2. État des Lieux & Exécution

### Résultat de l'exécution (Dernier Run)
Recette effectuée le : **{{ DATE }}**
Statut : **SUCCÈS (10/10 Tests passés)**

| ID Test | Composant | Scénario | Résultat |
| :--- | :--- | :--- | :--- |
| `test_models.py` | Modèles | Création Utilisateurs & Items | ✅ Passé |
| `test_auth.py` | Auth | Inscription, Login, Logout | ✅ Passé |
| `test_routes.py` | Routes | Protection pages (Login requis) | ✅ Passé |
| `test_delete.py` | CRUD | Suppression d'éléments | ✅ Passé |
| `test_flow.py` | **E2E** | **Parcours Critique Complet (Inscription Admin -> Ajout Article -> Vue Détail)** | ✅ Passé |

## 3. Détail du Parcours Critique (Automatisé)
Le fichier `tests/test_flow_complete.py` valide le scénario suivant :
1.  **Inscription** d'un nouvel administrateur (`qa_hero`) avec code secret.
2.  **Connexion** réussie et redirection vers Dashboard.
3.  **Ajout d'un Article** ("QA Test Item") avec quantité et numéro de série.
4.  **Vérification** : Récupération de l'article en base, accès à sa page de détail, validation de l'affichage du Serial Number.
5.  **Déconnexion**.

## 4. Recommandations QA & Sécurité
Suite à l'analyse du code et des tests :

1.  **Sécurité Headers** : L'application n'envoie pas les en-têtes de sécurité recommandés (HSTS, X-Frame-Options).
    *   *Action* : Installer `Flask-Talisman`.
2.  **Validation des Entrées** : Les formulaires utilisent `Flask-WTF`, ce qui est une bonne pratique pour éviter les CSRF.
3.  **Stockage des Images** : Vérifier que les uploads ne permettent pas d'écraser des fichiers système (le code utilise `werkzeug.secure_filename`, ce qui est bien).
4.  **Performance** : Ajouter des index sur les colonnes souvent recherchées (`item.name`, `item.serial_number`).

## 5. Comment lancer les tests
```bash
# Activer l'environnement virtuel et lancer pytest
./venv/Scripts/python -m pytest tests
```
