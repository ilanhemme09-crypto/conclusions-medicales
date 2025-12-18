"""
Backend API pour le système de conclusions médicales
FastAPI + Supabase
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from supabase import create_client, Client

# ============= CONFIGURATION =============
app = FastAPI(title="API Conclusions Médicales", version="1.0")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier le domaine exact
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connexion Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Variables d'environnement SUPABASE_URL et SUPABASE_KEY requises")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ============= MODÈLES PYDANTIC =============

class Categorie(BaseModel):
    id: str
    nom: str
    ordre: int

class Motif(BaseModel):
    id: str
    categorie_id: str
    titre: str
    ordre: int

class Bulle(BaseModel):
    mot: str
    info: str

class Proposition(BaseModel):
    placeholder: str
    suggestions: List[str]

class Module(BaseModel):
    type: str
    titre: str
    icon: str
    contenu: str
    bulles: List[Bulle]
    propositions: List[Proposition]

class Ordonnance(BaseModel):
    id: str
    categorie_ordo: str
    titre: str
    contenu: str
    bulles: List[Bulle]
    propositions: List[Proposition]

class CodeCCAM(BaseModel):
    code: str
    libelle: str

class FusionRequest(BaseModel):
    motif_principal_id: str
    motifs_secondaires_ids: List[str] = []

class FusionResponse(BaseModel):
    modules: List[Module]
    ordonnances: List[Ordonnance]
    codes_ccam: List[CodeCCAM]


# ============= ROUTES =============

@app.get("/")
def root():
    """Page d'accueil de l'API"""
    return {
        "message": "API Conclusions Médicales",
        "version": "1.0",
        "endpoints": {
            "categories": "/categories",
            "motifs": "/motifs?categorie_id={id}",
            "fusion": "/fusion (POST)"
        }
    }


@app.get("/categories", response_model=List[Categorie])
def get_categories():
    """Récupère toutes les catégories"""
    try:
        response = supabase.table("categories").select("*").order("ordre").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@app.get("/motifs", response_model=List[Motif])
def get_motifs(categorie_id: str):
    """Récupère les motifs d'une catégorie"""
    try:
        response = supabase.table("motifs")\
            .select("*")\
            .eq("categorie_id", categorie_id)\
            .order("ordre")\
            .execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@app.post("/fusion", response_model=FusionResponse)
def fusion_motifs(request: FusionRequest):
    """
    Fusionne un motif principal avec des motifs secondaires
    Retourne les modules, ordonnances et codes CCAM fusionnés
    """
    try:
        motifs_ids = [request.motif_principal_id] + request.motifs_secondaires_ids
        
        # Récupération de tous les modules
        modules_data = {}
        for motif_id in motifs_ids:
            modules_response = supabase.table("modules")\
                .select("*, bulles_info(*), propositions(*)")\
                .eq("motif_id", motif_id)\
                .execute()
            
            for module in modules_response.data:
                type_module = module['type_module']
                if type_module not in modules_data:
                    modules_data[type_module] = []
                modules_data[type_module].append(module)
        
        # Fusion des modules
        modules_fusionnes = []
        types_modules = [
            ('diagnostic', 'DIAGNOSTIC', '🔍'),
            ('signes_gravite', 'SIGNES DE GRAVITÉ', '⚠️'),
            ('aux_urgences', 'AUX URGENCES', '🏥'),
            ('conduite_tenir', 'CONDUITE À TENIR', '📋'),
            ('conseils', 'CONSEILS', '💡'),
            ('suivi', 'SUIVI', '📅'),
            ('consignes_reconsultation', 'CONSIGNES DE RECONSULTATION', '🚨')
        ]
        
        for type_key, titre, icon in types_modules:
            if type_key in modules_data:
                module_fusionne = fusionner_module(
                    type_key, 
                    titre, 
                    icon, 
                    modules_data[type_key]
                )
                if module_fusionne['contenu'].strip():
                    modules_fusionnes.append(module_fusionne)
        
        # Récupération des ordonnances
        ordonnances = []
        ordos_vues = set()  # Pour éviter les doublons
        
        for motif_id in motifs_ids:
            ordos_response = supabase.table("ordonnances")\
                .select("*, ordonnances_bulles(*), ordonnances_propositions(*)")\
                .eq("motif_id", motif_id)\
                .order("ordre")\
                .execute()
            
            for ordo in ordos_response.data:
                # Clé unique : catégorie + titre
                cle = f"{ordo['categorie_ordo']}_{ordo['titre']}"
                if cle not in ordos_vues:
                    ordos_vues.add(cle)
                    ordonnances.append({
                        "id": ordo['id'],
                        "categorie_ordo": ordo['categorie_ordo'],
                        "titre": ordo['titre'],
                        "contenu": ordo['contenu'],
                        "bulles": [
                            {"mot": b['position_mot'], "info": b['texte_info']}
                            for b in ordo.get('ordonnances_bulles', [])
                        ],
                        "propositions": [
                            {
                                "placeholder": p['champ_modifiable'],
                                "suggestions": p['suggestions']
                            }
                            for p in ordo.get('ordonnances_propositions', [])
                        ]
                    })
        
        # Tri des ordonnances par catégorie
        ordonnances.sort(key=lambda x: (x['categorie_ordo'], x['titre']))
        
        # Récupération des codes CCAM
        codes_ccam = []
        codes_vus = set()
        
        for motif_id in motifs_ids:
            ccam_response = supabase.table("codes_ccam")\
                .select("*")\
                .eq("motif_id", motif_id)\
                .order("ordre")\
                .execute()
            
            for code in ccam_response.data:
                if code['code'] not in codes_vus:
                    codes_vus.add(code['code'])
                    codes_ccam.append({
                        "code": code['code'],
                        "libelle": code['libelle']
                    })
        
        return {
            "modules": modules_fusionnes,
            "ordonnances": ordonnances,
            "codes_ccam": codes_ccam
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur fusion: {str(e)}")


# ============= FONCTIONS DE FUSION =============

def fusionner_module(type_key: str, titre: str, icon: str, modules: List[Dict]) -> Dict[str, Any]:
    """
    Fusionne plusieurs modules du même type selon la logique métier
    """
    
    if type_key == 'diagnostic':
        # Concaténation avec séparation par phrases
        contenus = []
        bulles_map = {}
        propositions_map = {}
        
        for module in modules:
            contenu = module['contenu'].strip()
            if contenu and contenu not in contenus:  # Éviter doublons
                contenus.append(contenu)
            
            # Bulles
            for bulle in module.get('bulles_info', []):
                bulles_map[bulle['position_mot']] = bulle['texte_info']
            
            # Propositions
            for prop in module.get('propositions', []):
                if prop['champ_modifiable'] not in propositions_map:
                    propositions_map[prop['champ_modifiable']] = prop['suggestions']
        
        return {
            "type": type_key,
            "titre": titre,
            "icon": icon,
            "contenu": " ".join(contenus),
            "bulles": [
                {"mot": mot, "info": info} 
                for mot, info in bulles_map.items()
            ],
            "propositions": [
                {"placeholder": ph, "suggestions": sugg}
                for ph, sugg in propositions_map.items()
            ]
        }
    
    elif type_key == 'signes_gravite':
        # Union des signes (liste à puces)
        signes = set()
        for module in modules:
            # Séparer par ligne ou par virgule
            contenu = module['contenu']
            for signe in contenu.split('\n'):
                signe = signe.strip().lstrip('-•▪').strip()
                if signe:
                    signes.add(signe)
        
        contenu_fusionne = "\n".join(f"- {s}" for s in sorted(signes))
        
        return {
            "type": type_key,
            "titre": titre,
            "icon": icon,
            "contenu": contenu_fusionne,
            "bulles": [],
            "propositions": []
        }
    
    elif type_key == 'conduite_tenir':
        # Format numéroté
        actions = []
        for module in modules:
            contenu = module['contenu']
            # Séparer les actions
            for ligne in contenu.split('\n'):
                ligne = ligne.strip().lstrip('0123456789.-) ').strip()
                if ligne and ligne not in actions:
                    actions.append(ligne)
        
        # Numérotation
        contenu_fusionne = "\n".join(
            f"{i+1} - {action}" 
            for i, action in enumerate(actions)
        )
        
        # Fusionner bulles et propositions
        bulles_map = {}
        propositions_map = {}
        for module in modules:
            for bulle in module.get('bulles_info', []):
                bulles_map[bulle['position_mot']] = bulle['texte_info']
            for prop in module.get('propositions', []):
                if prop['champ_modifiable'] not in propositions_map:
                    propositions_map[prop['champ_modifiable']] = prop['suggestions']
        
        return {
            "type": type_key,
            "titre": titre,
            "icon": icon,
            "contenu": contenu_fusionne,
            "bulles": [
                {"mot": mot, "info": info} 
                for mot, info in bulles_map.items()
            ],
            "propositions": [
                {"placeholder": ph, "suggestions": sugg}
                for ph, sugg in propositions_map.items()
            ]
        }
    
    else:
        # Fusion standard (conseils, suivi, etc.)
        contenus = []
        bulles_map = {}
        propositions_map = {}
        
        for module in modules:
            contenu = module['contenu'].strip()
            if contenu and contenu not in contenus:
                contenus.append(contenu)
            
            for bulle in module.get('bulles_info', []):
                bulles_map[bulle['position_mot']] = bulle['texte_info']
            for prop in module.get('propositions', []):
                if prop['champ_modifiable'] not in propositions_map:
                    propositions_map[prop['champ_modifiable']] = prop['suggestions']
        
        return {
            "type": type_key,
            "titre": titre,
            "icon": icon,
            "contenu": "\n\n".join(contenus),
            "bulles": [
                {"mot": mot, "info": info} 
                for mot, info in bulles_map.items()
            ],
            "propositions": [
                {"placeholder": ph, "suggestions": sugg}
                for ph, sugg in propositions_map.items()
            ]
        }


# ============= ROUTE DE TEST =============

@app.get("/health")
def health_check():
    """Vérification de l'état de l'API"""
    try:
        # Test connexion Supabase
        supabase.table("categories").select("count").limit(1).execute()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
