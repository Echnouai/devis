import streamlit as st
import requests
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from datetime import datetime
import io
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Estimation Devis · Tasmim Web", page_icon="💼", layout="wide")

# ── FONTS + CSS CUSTOM ───────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=DM+Sans:wght@400;500;700&display=swap');

    html, body, [class*="css"]  { font-family: 'Plus Jakarta Sans', -apple-system, sans-serif; }

    :root {
        --accent: #E85D30;
        --accent-dark: #c94a20;
        --accent-soft: #fff0e9;
        --ink: #14171f;
        --ink-soft: #5a6380;
        --surface: #ffffff;
        --surface-alt: #f6f7fb;
        --border: #ecedf2;
        --blue: #3d7ab5;
    }

    .stApp {
        background: radial-gradient(circle at 15% 0%, #fdf1ec 0%, #f6f7fb 35%, #f3f4f8 100%);
    }

    /* Hide default streamlit chrome for a cleaner feel */
    #MainMenu, footer, header { visibility: hidden; }

    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1180px; }

    /* ── Header ─────────────────────────────────────────── */
    .main-header {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, #14171f 0%, #232a3d 55%, #2d3448 100%);
        padding: 2.75rem 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 45px -20px rgba(20, 23, 31, 0.45);
    }
    .main-header::before {
        content: "";
        position: absolute;
        top: -60%; right: -10%;
        width: 420px; height: 420px;
        background: radial-gradient(circle, rgba(232,93,48,0.35) 0%, rgba(232,93,48,0) 70%);
        border-radius: 50%;
    }
    .main-header::after {
        content: "";
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 5px;
        background: linear-gradient(180deg, var(--accent), var(--accent-dark));
    }
    .main-header-eyebrow {
        color: var(--accent);
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        position: relative;
        z-index: 1;
    }
    .main-header h1 {
        color: white;
        font-size: 2.15rem;
        font-weight: 800;
        margin: 0.4rem 0 0.5rem 0;
        letter-spacing: -0.01em;
        position: relative;
        z-index: 1;
    }
    .main-header p {
        color: #aab0c0;
        margin: 0;
        font-size: 1rem;
        max-width: 560px;
        position: relative;
        z-index: 1;
    }
    .main-header span { color: var(--accent); font-weight: 700; }

    /* ── Section cards ──────────────────────────────────── */
    .section-card {
        background: var(--surface);
        border-radius: 16px;
        padding: 1.75rem 1.75rem 0.5rem 1.75rem;
        margin-bottom: 1rem;
        border: 1px solid var(--border);
        box-shadow: 0 2px 10px rgba(20, 23, 31, 0.04);
    }
    .section-title {
        color: var(--ink);
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 1.1rem;
        padding-bottom: 0.6rem;
        border-bottom: 2px solid var(--accent);
        display: inline-block;
    }

    /* ── Result / price card ────────────────────────────── */
    .price-card {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%);
        border-radius: 20px;
        padding: 2.25rem;
        text-align: center;
        color: white;
        margin-bottom: 1.25rem;
        box-shadow: 0 18px 40px -18px rgba(232, 93, 48, 0.55);
    }
    .price-card::before {
        content: "";
        position: absolute;
        top: -50%; left: -20%;
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(255,255,255,0.18) 0%, rgba(255,255,255,0) 70%);
        border-radius: 50%;
    }
    .price-label {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        opacity: 0.9;
        text-transform: uppercase;
        position: relative; z-index: 1;
    }
    .price-value {
        font-family: 'DM Sans', sans-serif;
        font-size: 3.6rem;
        font-weight: 800;
        line-height: 1.1;
        margin: 0.35rem 0;
        position: relative; z-index: 1;
    }
    .price-range {
        font-size: 0.95rem;
        opacity: 0.9;
        position: relative; z-index: 1;
    }

    /* ── Option badges ──────────────────────────────────── */
    .option-active {
        background: var(--accent-soft);
        color: var(--accent-dark);
        border: 1.5px solid var(--accent);
        border-radius: 20px;
        padding: 5px 13px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin: 3px;
    }
    .option-inactive {
        background: var(--surface-alt);
        color: #b3b8c9;
        border: 1.5px solid var(--border);
        border-radius: 20px;
        padding: 5px 13px;
        font-size: 0.8rem;
        display: inline-block;
        margin: 3px;
    }

    /* ── Buttons ─────────────────────────────────────────── */
    .stFormSubmitButton button {
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.85rem 2rem !important;
        font-size: 1.02rem !important;
        font-weight: 700 !important;
        width: 100% !important;
        letter-spacing: 0.01em;
        transition: all 0.2s ease !important;
        box-shadow: 0 10px 25px -8px rgba(232, 93, 48, 0.55) !important;
    }
    .stFormSubmitButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 14px 28px -8px rgba(232, 93, 48, 0.65) !important;
    }

    .stButton button {
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    /* ── Metrics ─────────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: var(--surface);
        border-radius: 14px;
        padding: 1.1rem 1rem;
        border: 1px solid var(--border);
        box-shadow: 0 2px 10px rgba(20, 23, 31, 0.04);
    }
    [data-testid="stMetricLabel"] { color: var(--ink-soft); font-weight: 600; }
    [data-testid="stMetricValue"] { color: var(--ink); font-family: 'DM Sans', sans-serif; }

    /* ── Inputs ──────────────────────────────────────────── */

    /* Selectbox: light background, dark text (the closed/collapsed box) */
    .stSelectbox > div > div,
    div[data-baseweb="select"] > div {
        border-radius: 10px !important;
        border-color: var(--border) !important;
        background: var(--surface) !important;
        color: var(--ink) !important;
    }
    div[data-baseweb="select"] * {
        color: var(--ink) !important;
        opacity: 1 !important;
    }

    /* Selectbox dropdown list (popover) — force LIGHT background + dark text,
       this was previously dark-on-dark and unreadable */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] div[role="listbox"] {
        background: var(--surface) !important;
    }
    div[data-baseweb="popover"] li,
    div[data-baseweb="popover"] li[role="option"] {
        background: var(--surface) !important;
        color: var(--ink) !important;
        opacity: 1 !important;
    }
    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="popover"] li[aria-selected="true"] {
        background: var(--accent-soft) !important;
        color: var(--accent-dark) !important;
    }

    /* Number input: dark pill with white text, high contrast in both directions */
    .stNumberInput > div > div {
        border-radius: 10px !important;
        border: none !important;
        background: var(--ink) !important;
    }
    .stNumberInput input {
        background: var(--ink) !important;
        color: #ffffff !important;
        opacity: 1 !important;
    }
    .stNumberInput button {
        background: var(--ink) !important;
        color: #ffffff !important;
        border-color: rgba(255,255,255,0.15) !important;
    }

    .stCheckbox { padding: 0.15rem 0; }
    label { color: var(--ink) !important; font-weight: 500 !important; }

    /* Checkbox labels (the option text next to each checkbox) */
    .stCheckbox p, .stCheckbox span, .stCheckbox div {
        color: var(--ink) !important;
        opacity: 1 !important;
        font-weight: 500 !important;
    }

    /* Generic fallback: any faded/disabled-looking text inside the form,
       excluding number input fields which intentionally stay white-on-dark */
    [data-testid="stForm"] p,
    [data-testid="stForm"] span,
    [data-testid="stForm"] label {
        color: var(--ink) !important;
        opacity: 1 !important;
    }

    /* ── Download button ─────────────────────────────────── */
    .stDownloadButton button {
        background: var(--ink) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        width: 100% !important;
        padding: 0.85rem !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }
    .stDownloadButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 22px -8px rgba(20, 23, 31, 0.4) !important;
    }

    /* ── Dataframe ───────────────────────────────────────── */
    .stDataFrame { border-radius: 12px; overflow: hidden; border: 1px solid var(--border); }

    /* ── Alerts (Analyse IA box) ─────────────────────────── */
    div[data-testid="stAlertContainer"] {
        border-radius: 12px !important;
        border-left: 4px solid var(--blue) !important;
        background: #eef4fa !important;
    }

    /* ── Divider ─────────────────────────────────────────── */
    hr { border-color: var(--border); }

    /* Caption */
    .stCaption, [data-testid="stCaptionContainer"] { color: var(--ink-soft) !important; }
</style>
""", unsafe_allow_html=True)

# ── HEADER ───────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <div class="main-header-eyebrow">Estimation intelligente</div>
    <h1>💼 IA d'estimation automatique de devis</h1>
    <p>Remplissez les critères du projet pour obtenir une estimation instantanée par <span>Tasmim Web</span></p>
</div>
""", unsafe_allow_html=True)

# ── FORMULAIRE ───────────────────────────────────────────────
with st.form("devis_form"):

    col_left, col_right = st.columns([1.2, 1], gap="large")

    with col_left:
        
        st.markdown('<p class="section-title">Informations du projet</p>', unsafe_allow_html=True)
        type_site = st.selectbox("Type de site", ["Site Vitrine", "E-commerce", "Landing Page"])
        col_a, col_b = st.columns(2)
        with col_a:
            nb_pages = st.number_input("Nombre de pages", min_value=1, max_value=100, value=10)
        with col_b:
            delai_jours = st.number_input("Délai (jours)", min_value=7, max_value=180, value=30)
        niveau_design = st.selectbox("Niveau de design", ["Basic", "Standard", "Premium"])
        experience_client = st.selectbox("Type de client", ["New Client", "Returning Client", "VIP Client"])
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<p class="section-title">Options du projet</p>', unsafe_allow_html=True)
        col_o1, col_o2 = st.columns(2)
        with col_o1:
            seo             = st.checkbox("🔍 SEO")
            ecommerce       = st.checkbox("🛒 E-commerce")
            animations      = st.checkbox("✨ Animations")
            hebergement     = st.checkbox("🌐 Hébergement")
        with col_o2:
            paiement_en_ligne = st.checkbox("💳 Paiement en ligne")
            nom_domaine       = st.checkbox("🔗 Nom de domaine")
            multilingue       = st.checkbox("🌍 Multilingue")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("⚡ Estimer le prix maintenant", use_container_width=True)

# ── RÉSULTAT ─────────────────────────────────────────────────
if submitted:
    payload = {
        "type_site": type_site,
        "nb_pages": nb_pages,
        "niveau_design": niveau_design,
        "seo": int(seo),
        "ecommerce": int(ecommerce),
        "paiement_en_ligne": int(paiement_en_ligne),
        "animations": int(animations),
        "hebergement": int(hebergement),
        "nom_domaine": int(nom_domaine),
        "multilingue": int(multilingue),
        "delai_jours": delai_jours,
        "experience_client": experience_client
    }

    with st.spinner("⚙️ Analyse en cours par l'IA..."):
        response = requests.post("http://devis.up.railway.app/predict", json=payload)

    if response.status_code == 200:
        result = response.json()
        st.session_state["result"] = result
        st.session_state["payload"] = payload

        st.markdown("<br>", unsafe_allow_html=True)

        # Prix principal
        st.markdown(f"""
        <div class="price-card">
            <div class="price-label">Estimation du prix</div>
            <div class="price-value">{result['prix_estime']:,.0f} MAD</div>
            <div class="price-range">
                Fourchette : {result['fourchette_min']:,.0f} MAD — {result['fourchette_max']:,.0f} MAD
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Détail métriques
        c1, c2, c3 = st.columns(3)
        c1.metric("Prix estimé", f"{result['prix_estime']:,.0f} MAD")
        c2.metric("Minimum (-15%)", f"{result['fourchette_min']:,.0f} MAD")
        c3.metric("Maximum (+15%)", f"{result['fourchette_max']:,.0f} MAD")

        st.markdown("<br>", unsafe_allow_html=True)

        # Explication LLM + SHAP côte à côte
        col_exp, col_shap = st.columns([1, 1], gap="large")

        with col_exp:
            
            st.markdown('<p class="section-title">Analyse IA</p>', unsafe_allow_html=True)
            st.info(result["explication"])
            st.markdown('</div>', unsafe_allow_html=True)

        with col_shap:
           
            st.markdown('<p class="section-title">Pourquoi ce prix ?</p>', unsafe_allow_html=True)
            if "shap_values" in result:
                shap_vals     = result["shap_values"]
                feature_names = result["feature_names"]
                df_shap = pd.DataFrame({
                    "Feature": feature_names,
                    "Impact": shap_vals
                }).sort_values("Impact", key=abs, ascending=True)

                fig, ax = plt.subplots(figsize=(7, 4))
                fig.patch.set_facecolor("white")
                bar_colors = ["#E85D30" if v > 0 else "#3d7ab5" for v in df_shap["Impact"]]
                ax.barh(df_shap["Feature"], df_shap["Impact"],
                        color=bar_colors, edgecolor="none", height=0.55)
                ax.axvline(0, color="#d8dae2", linewidth=1)
                ax.set_facecolor("white")
                for spine in ["top", "right", "left"]:
                    ax.spines[spine].set_visible(False)
                ax.tick_params(left=False)
                ax.set_xlabel("Impact sur le prix (MAD)", fontsize=9, color="#5a6380", fontweight="medium")
                ax.tick_params(axis="y", labelsize=9, colors="#14171f")
                ax.tick_params(axis="x", labelsize=8, colors="#5a6380")
                plt.tight_layout()
                st.pyplot(fig)
                st.caption("🔴 Rouge = augmente le prix  |  🔵 Bleu = diminue le prix")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("❌ Erreur lors de l'appel à l'API. Vérifiez que uvicorn est lancé.")

# ── PDF + HISTORIQUE ─────────────────────────────────────────
if "result" in st.session_state:
    result  = st.session_state["result"]
    payload = st.session_state["payload"]

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    col_pdf, col_hist = st.columns(2, gap="large")

    with col_pdf:
       
        st.markdown('<p class="section-title">Télécharger le devis</p>', unsafe_allow_html=True)

        def generate_pdf(payload, result):
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer, pagesize=A4,
                topMargin=2 * cm, bottomMargin=2 * cm,
                leftMargin=2 * cm, rightMargin=2 * cm
            )
            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                "TitleCustom", parent=styles["Heading1"],
                fontSize=20, textColor=colors.HexColor("#14171f"),
                spaceAfter=4
            )
            subtitle_style = ParagraphStyle(
                "SubtitleCustom", parent=styles["Normal"],
                fontSize=10, textColor=colors.HexColor("#5a6380"),
                spaceAfter=18
            )
            section_style = ParagraphStyle(
                "SectionCustom", parent=styles["Heading2"],
                fontSize=12, textColor=colors.HexColor("#E85D30"),
                spaceBefore=14, spaceAfter=8
            )
            body_style = ParagraphStyle(
                "BodyCustom", parent=styles["Normal"],
                fontSize=10, textColor=colors.HexColor("#14171f"),
                leading=15
            )

            elements = []
            elements.append(Paragraph("Devis estimatif — Tasmim Web", title_style))
            elements.append(Paragraph(
                f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
                subtitle_style
            ))
            elements.append(HRFlowable(width="100%", color=colors.HexColor("#E85D30"), thickness=1.2))
            elements.append(Spacer(1, 0.5 * cm))

            # Détails du projet
            elements.append(Paragraph("Détails du projet", section_style))
            options_actives = []
            option_map = {
                "seo": "SEO", "ecommerce": "E-commerce",
                "paiement_en_ligne": "Paiement en ligne", "animations": "Animations",
                "hebergement": "Hébergement", "nom_domaine": "Nom de domaine",
                "multilingue": "Multilingue"
            }
            for key, label in option_map.items():
                if payload.get(key):
                    options_actives.append(label)

            details_data = [
                ["Type de site", payload.get("type_site", "-")],
                ["Nombre de pages", str(payload.get("nb_pages", "-"))],
                ["Niveau de design", payload.get("niveau_design", "-")],
                ["Type de client", payload.get("experience_client", "-")],
                ["Délai (jours)", str(payload.get("delai_jours", "-"))],
                ["Options incluses", ", ".join(options_actives) if options_actives else "Aucune"],
            ]
            details_table = Table(details_data, colWidths=[5 * cm, 10.5 * cm])
            details_table.setStyle(TableStyle([
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#5a6380")),
                ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#14171f")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.HexColor("#ecedf2")),
            ]))
            elements.append(details_table)
            elements.append(Spacer(1, 0.6 * cm))

            # Estimation
            elements.append(Paragraph("Estimation", section_style))
            estim_data = [
                ["Prix estimé", f"{result['prix_estime']:,.0f} MAD"],
                ["Fourchette basse (-15%)", f"{result['fourchette_min']:,.0f} MAD"],
                ["Fourchette haute (+15%)", f"{result['fourchette_max']:,.0f} MAD"],
            ]
            estim_table = Table(estim_data, colWidths=[7 * cm, 8.5 * cm])
            estim_table.setStyle(TableStyle([
                ("FONTSIZE", (0, 0), (-1, -1), 10.5),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#5a6380")),
                ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#14171f")),
                ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (1, 0), (1, 0), 13),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.HexColor("#ecedf2")),
            ]))
            elements.append(estim_table)
            elements.append(Spacer(1, 0.6 * cm))

            # Analyse IA
            if result.get("explication"):
                elements.append(Paragraph("Analyse IA", section_style))
                elements.append(Paragraph(result["explication"], body_style))
                elements.append(Spacer(1, 0.4 * cm))

            elements.append(Spacer(1, 1 * cm))
            elements.append(HRFlowable(width="100%", color=colors.HexColor("#ecedf2"), thickness=0.8))
            elements.append(Spacer(1, 0.3 * cm))
            elements.append(Paragraph(
                "Ce document est une estimation indicative et ne constitue pas un engagement contractuel final.",
                ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8, textColor=colors.HexColor("#9aa0b3"))
            ))

            doc.build(elements)
            buffer.seek(0)
            return buffer

        pdf_buffer = generate_pdf(payload, result)
        if pdf_buffer:
            st.download_button(
                label="📄 Télécharger le devis PDF",
                data=pdf_buffer,
                file_name=f"devis_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_hist:
        
        st.markdown('<p class="section-title">Historique des devis</p>', unsafe_allow_html=True)
        if st.button("📋 Afficher l'historique", use_container_width=True):
            with st.spinner("Chargement..."):
                try:
                    response_history = requests.get("http://devis.up.railway.app/history", timeout=10)
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Impossible de contacter l'API (uvicorn est-il lancé ?) : {e}")
                    response_history = None

                if response_history is not None:
                    if response_history.status_code == 200:
                        try:
                            historique = response_history.json()
                        except ValueError:
                            st.error("❌ Réponse de l'API invalide (JSON illisible).")
                            historique = None

                        if historique is not None:
                            if len(historique) == 0:
                                st.info("Aucun devis dans l'historique.")
                            else:
                                expected_cols = ["ID", "Type de site", "Nb pages",
                                                  "Prix estimé (MAD)", "Fourchette min",
                                                  "Fourchette max", "Date"]

                                # historique peut être une liste de listes (rows) OU
                                # une liste de dicts selon l'API — on gère les deux.
                                first_row = historique[0]
                                if isinstance(first_row, dict):
                                    df_history = pd.DataFrame(historique)
                                else:
                                    n_cols = len(first_row)
                                    cols = expected_cols[:n_cols] if n_cols <= len(expected_cols) \
                                        else expected_cols + [f"Col {i}" for i in range(len(expected_cols), n_cols)]
                                    df_history = pd.DataFrame(historique, columns=cols)

                                st.dataframe(df_history, use_container_width=True)
                    else:
                        st.error(f"❌ Erreur API ({response_history.status_code}) lors de la récupération de l'historique.")
        st.markdown('</div>', unsafe_allow_html=True)