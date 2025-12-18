# 🏥 Système de Conclusions Médicales

> Outil de génération automatique de comptes rendus médicaux pour les urgentistes, avec fusion intelligente de plusieurs motifs de consultation.

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
- [Déploiement](#déploiement)
- [Utilisation](#utilisation)
- [Structure des données](#structure-des-données)

---

## 🎯 Vue d'ensemble

Ce système permet aux médecins urgentistes de :
- Sélectionner un motif de consultation principal
- Ajouter des motifs secondaires (comorbidités)
- Générer automatiquement une conclusion médicale complète
- Fusionner intelligemment les différents modules (diagnostic, traitement, etc.)
- Accéder à des ordonnances types
- Visualiser les codes CCAM pertinents

**Technologies utilisées :**
- **Frontend** : HTML, CSS, JavaScript (vanilla)
- **Backend** : Python FastAPI
- **Base de données** : Supabase (PostgreSQL)
- **Déploiement** : Render (backend), GitHub Pages ou Netlify (frontend)

---

## ✨ Fonctionnalités

### 🎨 Interface utilisateur
- Design moderne avec gradients et animations
- Sélection intuitive des catégories et motifs
- Distinction visuelle motif principal / secondaires

### 💡 Enrichissement du contenu
- **Bulles d'information** : icônes 💡 cliquables avec explications détaillées
- **Champs modifiables** : placeholders XXXX avec suggestions contextuelles
- **Propositions dynamiques** : menu déroulant pour compléter rapidement

### 📋 Modules médicaux
1. **Diagnostic** : description de la pathologie
2. **Signes de gravité** : éléments d'alerte
3. **Aux urgences** : examens réalisés
4. **Conduite à tenir** : protocole de soins (numéroté)
5. **Conseils** : recommandations au patient
6. **Suivi** : consultations à prévoir
7. **Consignes de reconsultation** : signes d'alerte

### 💊 Ordonnances types
- Bibliothèque d'ordonnances par catégorie
- Filtrage par type de médicament
- Copie rapide dans le presse-papier
- Support des bulles et propositions dans les ordonnances

### 📊 Codage médical
- Affichage automatique des codes CCAM
- Fusion des codes de tous les motifs sélectionnés
- Suppression des doublons

---

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │
│   (HTML/CSS/JS) │
└────────┬────────┘
         │
         │ HTTP REST API
         │
┌────────▼────────┐
│   Backend       │
│   (FastAPI)     │
└────────┬────────┘
         │
         │ Client Supabase
         │
┌────────▼────────┐
│   Supabase      │
│   (PostgreSQL)  │
└─────────────────┘
```

### Flux de données

1. **Chargement initial** : Le frontend récupère les catégories et les motifs via l'API
2. **Sélection** : L'utilisateur choisit un motif principal et des motifs secondaires
3. **Fusion** : Le backend fusionne les modules selon des règles métier
4. **Affichage** : Le frontend affiche la conclusion enrichie (bulles, propositions)

---

## 📦 Installation

### Prérequis

- Python 3.9+
- Compte Supabase (gratuit)
- Compte GitHub
- Compte Render (gratuit)

### 1. Cloner le projet

```bash
git clone https://github.com/votre-username/conclusions-medicales.git
cd conclusions-medicales
```

### 2. Installer les dépendances Python

```bash
cd backend
pip install -r requirements.txt
```

### 3. Créer un projet Supabase

1. Allez sur [supabase.com](https://supabase.com)
2. Créez un nouveau projet
3. Notez l'**URL du projet** et la **clé API anon**

### 4. Initialiser la base de données

1. Dans Supabase, allez dans **SQL Editor**
2. Copiez-collez le contenu de `supabase_init.sql`
3. Exécutez le script
4. Vérifiez que les tables sont créées dans **Table Editor**

### 5. Configurer les variables d'environnement

Créez un fichier `.env` dans le dossier `backend/` :

```env
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_KEY=votre-cle-anon-publique
```

### 6. Tester localement

```bash
cd backend
python main.py
```

L'API sera accessible sur `http://localhost:8000`

Ouvrez `frontend_api.html` dans votre navigateur (après avoir changé l'URL de l'API vers `http://localhost:8000`).

---

## 🚀 Déploiement

### Backend sur Render

1. **Créer un compte sur [Render](https://render.com)**

2. **Connecter votre dépôt GitHub**
   - Cliquez sur "New +" → "Web Service"
   - Connectez votre dépôt GitHub

3. **Configurer le service**
   - **Name** : `conclusions-medicales-api`
   - **Region** : choisir la plus proche
   - **Branch** : `main`
   - **Root Directory** : `backend`
   - **Runtime** : `Python 3`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Ajouter les variables d'environnement**
   - Allez dans "Environment"
   - Ajoutez :
     ```
     SUPABASE_URL=https://votre-projet.supabase.co
     SUPABASE_KEY=votre-cle-anon
     ```

5. **Déployer**
   - Cliquez sur "Create Web Service"
   - Attendez la fin du déploiement (5-10 minutes)
   - Notez l'URL de votre API : `https://conclusions-medicales-api.onrender.com`

### Frontend sur GitHub Pages / Netlify

#### Option A : GitHub Pages

1. Dans votre dépôt GitHub, allez dans **Settings** → **Pages**
2. Source : `Deploy from a branch`
3. Branch : `main` → `/root`
4. Cliquez sur "Save"

Votre site sera disponible sur `https://votre-username.github.io/conclusions-medicales/`

#### Option B : Netlify

1. Créez un compte sur [Netlify](https://netlify.com)
2. "Add new site" → "Import an existing project"
3. Connectez votre dépôt GitHub
4. Déployez

**IMPORTANT** : Dans tous les cas, mettez à jour l'URL de l'API dans `frontend_api.html` :

```javascript
// Ligne ~765
const API_URL = 'https://conclusions-medicales-api.onrender.com';
```

---

## 📖 Utilisation

### Pour les médecins

1. **Sélectionner une catégorie principale**
   - Cliquez sur une catégorie (ex: Cardiologie)
   - Les motifs de cette catégorie s'affichent

2. **Choisir le motif principal**
   - Cliquez sur le motif (ex: Douleur thoracique)
   - Il devient vert

3. **Ajouter des motifs secondaires** (optionnel)
   - Sélectionnez une catégorie secondaire
   - Cliquez sur les motifs à ajouter
   - Ils deviennent bleus

4. **Générer la conclusion**
   - Cliquez sur "✨ Générer la conclusion"
   - La conclusion apparaît à droite

5. **Personnaliser**
   - Cliquez sur les champs jaunes (XXXX) pour les compléter
   - Survolez les 💡 pour voir les explications
   - Cliquez sur "📋 Ordonnances" pour accéder aux prescriptions

6. **Copier**
   - Cliquez sur "📋 Copier" pour copier toute la conclusion
   - Collez dans votre logiciel de dossier patient

### Raccourcis clavier

- `Entrée` : Valider une saisie dans un champ XXXX
- `Échap` : Fermer les modales

---

## 🗄️ Structure des données

### Tables Supabase

```
categories
├─ motifs
   ├─ modules
   │  ├─ bulles_info
   │  └─ propositions
   ├─ ordonnances
   │  ├─ ordonnances_bulles
   │  └─ ordonnances_propositions
   └─ codes_ccam
```

### Types de modules

| Type | Description | Exemple |
|------|-------------|---------|
| `diagnostic` | Conclusion diagnostique | "Douleur thoracique atypique" |
| `signes_gravite` | Signes d'alerte | "Pas de signe de gravité" |
| `aux_urgences` | Examens réalisés | "ECG normal, Troponine négative" |
| `conduite_tenir` | Protocole de soins | "1 - Repos, 2 - Antalgiques" |
| `conseils` | Recommandations | "Éviter les efforts" |
| `suivi` | Consultations à prévoir | "Consultation médecin traitant sous 7j" |
| `consignes_reconsultation` | Signes d'alerte | "Reconsulter si douleur intense" |

---

## 🔧 Personnalisation

### Ajouter une nouvelle catégorie

```sql
INSERT INTO categories (nom, ordre) VALUES ('Pédiatrie', 7);
```

### Ajouter un nouveau motif

```sql
INSERT INTO motifs (categorie_id, titre, ordre) 
VALUES (
    (SELECT id FROM categories WHERE nom = 'Pédiatrie'),
    'Fièvre du nourrisson',
    1
);
```

### Ajouter un module

```sql
INSERT INTO modules (motif_id, type_module, contenu, ordre)
VALUES (
    (SELECT id FROM motifs WHERE titre = 'Fièvre du nourrisson'),
    'diagnostic',
    'Fièvre isolée sans point d''appel infectieux.',
    1
);
```

### Ajouter une bulle d'information

```sql
INSERT INTO bulles_info (module_id, position_mot, texte_info)
VALUES (
    (SELECT id FROM modules WHERE contenu LIKE '%isolée%'),
    'isolée',
    'Absence de signes de localisation : pas de rhinite, pas de diarrhée, examen clinique normal.'
);
```

---

## 🛠️ Développement

### Lancer en mode développement

**Backend :**
```bash
cd backend
uvicorn main:app --reload
```

**Frontend :**
Ouvrir `frontend_api.html` directement dans le navigateur, ou utiliser un serveur local :
```bash
python -m http.server 8080
```

### Tester l'API

```bash
# Health check
curl http://localhost:8000/health

# Récupérer les catégories
curl http://localhost:8000/categories

# Récupérer les motifs d'une catégorie
curl http://localhost:8000/motifs?categorie_id=UUID

# Fusionner des motifs
curl -X POST http://localhost:8000/fusion \
  -H "Content-Type: application/json" \
  -d '{
    "motif_principal_id": "UUID",
    "motifs_secondaires_ids": ["UUID1", "UUID2"]
  }'
```

### Structure des fichiers

```
.
├── backend/
│   ├── main.py              # Application FastAPI
│   ├── requirements.txt     # Dépendances Python
│   └── .env                 # Variables d'environnement (à créer)
│
├── frontend_api.html        # Interface utilisateur
├── supabase_init.sql        # Script d'initialisation BDD
├── ARCHITECTURE.md          # Documentation architecture
└── README.md               # Ce fichier
```

---

## 🐛 Dépannage

### L'API ne se connecte pas

1. Vérifiez que le backend est démarré : `http://localhost:8000/health`
2. Vérifiez les variables d'environnement dans `.env`
3. Testez la connexion Supabase :
   ```python
   from supabase import create_client
   supabase = create_client("URL", "KEY")
   print(supabase.table("categories").select("*").execute())
   ```

### Les données ne s'affichent pas

1. Vérifiez que les tables existent dans Supabase (Table Editor)
2. Vérifiez que les données sont insérées :
   ```sql
   SELECT COUNT(*) FROM categories;
   SELECT COUNT(*) FROM motifs;
   ```
3. Vérifiez les policies RLS (Row Level Security)

### CORS Error

Si vous voyez une erreur CORS dans la console :
1. Vérifiez que le backend autorise l'origine du frontend
2. Mettez à jour `main.py` :
   ```python
   allow_origins=["https://votre-domaine.com"]
   ```

---

## 📝 TODO / Améliorations futures

- [ ] Authentification utilisateurs (Supabase Auth)
- [ ] Historique des conclusions générées
- [ ] Export PDF
- [ ] Templates personnalisables par utilisateur
- [ ] Suggestions IA de motifs secondaires pertinents
- [ ] Statistiques d'utilisation
- [ ] Version mobile (Progressive Web App)
- [ ] Intégration avec logiciels de dossiers patients

---

## 👥 Contribution

Les contributions sont les bienvenues ! 

1. Fork le projet
2. Créez une branche (`git checkout -b feature/amelioration`)
3. Committez vos changements (`git commit -m 'Ajout fonctionnalité X'`)
4. Pushez (`git push origin feature/amelioration`)
5. Ouvrez une Pull Request

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 📞 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Consulter la documentation dans `ARCHITECTURE.md`

---

## 🙏 Remerciements

Merci aux urgentistes qui ont contribué à définir les besoins et tester l'outil.

---

**Version** : 1.0  
**Dernière mise à jour** : Décembre 2024
