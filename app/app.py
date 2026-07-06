import streamlit as st
import requests
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
    )
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from datetime import datetime
import io

#page configuration
st.set_page_config(
    page_title="Estimation Devis",
    page_icon=":bar_chart:",
    layout="centered",
)
st.title("IA d'estimation automatique de devis")
st.markdown("Remplissez les critères du projet pour obtenir une estimation instantanée.")

#creation de formulaire
with st.form("devis_form"):
    col1,col2=st.columns(2)
    with col1:
        type_site=st.selectbox(
            "Type de site web",
            ["Site vitrine", "Site e-commerce", "Landing page"]
        )
        nb_pages=st.number_input(
            "Nombre de pages",
            min_value=1,
            max_value=100,
            value=10
        )
        niveau_desin=st.selectbox(
            "Niveau de design",
            ["Basique", "Standard", "Premium"]
        )
        delai_jours=st.number_input(
            "Délai de livraison (en jours)",
            min_value=1,
            max_value=365,
            value=30
        )
        experience_client=st.selectbox(
            "Expérience client",
            ["New Client", "Returning Client", "VIP Client"]
        )
        
    with col2:
        seo=st.checkbox("SEO")
        ecommerce=st.checkbox("E-commerce")
        paiement_en_ligne=st.checkbox("Paiement en ligne")
        animation=st.checkbox("Animation")
        hebergement=st.checkbox("Hébergement")
        nom_domaine=st.checkbox("Nom de domaine")
        multilingue=st.checkbox("Multilingue")
        
    
    submitted=st.form_submit_button("Estimer le prix", use_container_width=True)

#appeler l api et afficher le résultat
if submitted:
    payload={
        "type_site": type_site,
        "nb_pages": nb_pages,
        "niveau_desin": niveau_desin,
        "delai_jours": delai_jours,
        "experience_client": experience_client,
        "seo":int(seo),
        "ecommerce": int(ecommerce),
        "paiement_en_ligne": int(paiement_en_ligne),
        "animation": int(animation),
        "hebergement": int(hebergement),
        "nom_domaine": int(nom_domaine),
        "multilingue": int(multilingue)
    }
    with st.spinner("Estimation en cours..."):
        response=requests.post("http://127.0.0.1:8000/predict", json=payload)
        if response.status_code == 200:
            result=response.json()
            st.success("Estimation terminée !")
            col1,col2,col3=st.columns(3)
            col1.metric("Prix estimé", f"{result['prix_estime']: ,.0f} MAD")
            col2.metric("Minimum", f"{result['fourchette_min']: ,.0f} MAD")
            col3.metric("Maximum", f"{result['fourchette_max']: ,.0f} MAD")
        
            st.markdown("##########Explication")
            st.info(result['explication'])
            #stocker le resultat pour PDF
            st.session_state['result']=result
            st.session_state['payload']=payload
        else:
            st.error("Erreur lors de l'appel à l'API.")
#creation de pdf
if "result" in st.session_state:
    result = st.session_state["result"]
    payload = st.session_state["payload"]

    def generate_pdf():
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()
        ORANGE = colors.HexColor("#E85D30")
        DARK = colors.HexColor("#1a1f2b")
        GRAY = colors.HexColor("#5a6380")

        story = []

        # En-tête
        story.append(Paragraph("TASMIM WEB", ParagraphStyle("ey", fontSize=9,
            fontName="Helvetica-Bold", textColor=ORANGE)))
        story.append(Paragraph("Devis estimé par IA", ParagraphStyle("ti", fontSize=20,
            fontName="Helvetica-Bold", textColor=DARK, spaceAfter=4)))
        story.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
            ParagraphStyle("sm", fontSize=9, textColor=GRAY)))
        story.append(HRFlowable(width="100%", thickness=2, color=ORANGE, spaceAfter=16))

        # Prix
        story.append(Paragraph("Prix estimé", ParagraphStyle("lb", fontSize=10,
            fontName="Helvetica-Bold", textColor=GRAY)))
        story.append(Paragraph(f"{result['prix_estime']:,.0f} MAD",
            ParagraphStyle("pr", fontSize=28, fontName="Helvetica-Bold", textColor=ORANGE)))
        story.append(Paragraph(
            f"Fourchette : {result['fourchette_min']:,.0f} — {result['fourchette_max']:,.0f} MAD",
            ParagraphStyle("fo", fontSize=10, textColor=GRAY, spaceAfter=16)))

        # Critères
        story.append(Paragraph("Critères du projet", ParagraphStyle("sec", fontSize=13,
            fontName="Helvetica-Bold", textColor=DARK, spaceBefore=12, spaceAfter=8)))
        story.append(HRFlowable(width="100%", thickness=0.5,
            color=colors.HexColor("#e0e0e0"), spaceAfter=8))

        criteres = [
            ["Type de site", payload["type_site"]],
            ["Nombre de pages", str(payload["nb_pages"])],
            ["Niveau de design", payload["niveau_design"]],
            ["Délai", f"{payload['delai_jours']} jours"],
            ["Client", payload["experience_client"]],
            ["SEO", "Oui" if payload["seo"] else "Non"],
            ["E-commerce", "Oui" if payload["ecommerce"] else "Non"],
            ["Paiement en ligne", "Oui" if payload["paiement_en_ligne"] else "Non"],
            ["Animations", "Oui" if payload["animations"] else "Non"],
            ["Multilingue", "Oui" if payload["multilingue"] else "Non"],
        ]

        table = Table(criteres, colWidths=[8*cm, 8*cm])
        table.setStyle(TableStyle([
            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 10),
            ("TEXTCOLOR", (0,0), (0,-1), GRAY),
            ("TEXTCOLOR", (1,0), (1,-1), DARK),
            ("ROWBACKGROUNDS", (0,0), (-1,-1),
                [colors.HexColor("#fafafa"), colors.white]),
            ("TOPPADDING", (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
            ("LEFTPADDING", (0,0), (-1,-1), 10),
            ("LINEBELOW", (0,-1), (-1,-1), 0.5, colors.HexColor("#eeeeee")),
        ]))
        story.append(table)

        # Explication
        story.append(Spacer(1, 16))
        story.append(Paragraph("Explication", ParagraphStyle("sec2", fontSize=13,
            fontName="Helvetica-Bold", textColor=DARK, spaceAfter=8)))
        story.append(HRFlowable(width="100%", thickness=0.5,
            color=colors.HexColor("#e0e0e0"), spaceAfter=8))
        story.append(Paragraph(result["explication"],
            ParagraphStyle("exp", fontSize=10, textColor=DARK, leading=16)))

        # Footer
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=ORANGE, spaceAfter=6))
        story.append(Paragraph(f"Tasmim Web · {datetime.now().strftime('%Y')}",
            ParagraphStyle("ft", fontSize=8, textColor=GRAY,
            alignment=1)))

        doc.build(story)
        buffer.seek(0)
        return buffer

    pdf_buffer = generate_pdf()
    st.download_button(
        label="Télécharger le devis en PDF",
        data=pdf_buffer,
        file_name=f"devis_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )