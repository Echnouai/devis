from fastapi import FastAPI
from schemas import DevisInput,DevisOutput
from model import predict
from database import init_db,save_devis
from groq import Groq

app=FastAPI(title="IA Estimation Devis")

init_db()

from dotenv import load_dotenv
import os

load_dotenv()

client_groq = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

@app.post("/predict",response_model=DevisOutput)
def get_prediction(data:DevisInput):
    result=predict(data.dict())
    prix=result["prix"]
    fourchette_min=round(prix*0.85,2)
    fourchette_max=round(prix*1.15,2)
    
    prompt=f"""
    Tu es un assistant commercial pour une agence web marocaine.
    Un client a demandé un devis avec ces critères :
    - Type de site : {data.type_site}
    - Nombre de pages : {data.nb_pages}
    - Niveau design : {data.niveau_design}
    - SEO : {'Oui' if data.seo else 'Non'}
    - E-commerce : {'Oui' if data.ecommerce else 'Non'}

    Le modèle ML a estimé le prix à {prix:,.0f} MAD.
    En 3-4 phrases professionnelles en français :
    1. Explique pourquoi ce prix est justifié
    2. Mentionne les options qui font monter le coût
    3. Donne un conseil au client
    """
    try:
      response = client_groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

      explication = response.choices[0].message.content

    except Exception as e:
      print("Groq error:", e)
      raise
    
    save_devis(data.type_site,data.nb_pages,prix)
    
    return DevisOutput(
        prix_estime=prix,fourchette_min=fourchette_min,
        fourchette_max=fourchette_max,
        explication=explication,
        shap_values=result["shap_values"],
        feature_names=result["feature_names"]
    )
    
@app.get("/history")
def get_history():
    import sqlite3
    conn=sqlite3.connect("historique.db")
    
    rows=conn.execute(
        "SELECT * FROM devis ORDER BY date DESC LIMIT 20"
    ).fetchall()
    conn.close()
    return rows
