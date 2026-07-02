from pydantic import BaseModel

class DevisInput(BaseModel):
    type_site:str
    nb_pages:int
    niveau_design:str
    seo:int
    ecommerce:int
    paiement_en_ligne:int
    animations:int
    hebergement:int
    nom_domaine:int
    delai_jours:int
    experience_client:str
    
class DevisOutput(BaseModel):
    prix_estime:float
    fourchette_min:float
    fourchette_max:float
    explication:str     