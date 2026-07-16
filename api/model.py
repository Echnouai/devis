import joblib
import numpy as np
from pathlib import Path
from sklearn.preprocessing import LabelEncoder

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "catboost_model.pkl"
model = joblib.load(MODEL_PATH)

le_type=LabelEncoder()
le_type.classes_=np.array(["E-commerce","Landing Page","Site Vitrine"])

le_niveau=LabelEncoder()
le_niveau.classes_=np.array(["Avancé", "Basic", "Premium", "Standard"])

le_experience = LabelEncoder()
le_experience.classes_ = np.array(["New Client", "Returning Client", "VIP Client"])
import shap
explainer = shap.TreeExplainer(model)
def predict(data:dict)-> float:
    import pandas as pd
    df=pd.DataFrame([data])
    df["type_site"]=le_type.transform(df["type_site"])
    df["niveau_design"]=le_niveau.transform(df["niveau_design"])
    df["experience_client"]=le_experience.transform(df["experience_client"])
    prix=float(model.predict(df)[0])
    shap_values = explainer.shap_values(df)
    return {
        "prix":prix,
        "shap_values":shap_values[0].tolist(),
        "feature_names":df.columns.tolist()
    }