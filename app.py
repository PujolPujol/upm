import streamlit as st
from affiche_upm import get_summary_from_url, create_affiche_style2
import uuid
import os

st.set_page_config(
    page_title="Générateur d’affiches UPM",
    layout="centered",
)

st.title("📰 Générateur d’affiches UPM")
st.markdown("Colle un lien d’article et une phrase d’accroche pour générer automatiquement une affiche prête à partager.")

url = st.text_input("🔗 URL de l'article")
accroche = st.text_input("📣 Phrase d'accroche", placeholder="EX : LISEZ L'ARTICLE DU MONDE")

if st.button("🎨 Générer l’affiche"):
    if url and accroche:
        try:
            with st.spinner("Récupération de l’article et génération de l’affiche…"):
                title, _ = get_summary_from_url(url)
                output = f"affiche_{uuid.uuid4().hex[:8]}.png"
                create_affiche_style2(title, accroche, output)
            st.success("✅ Affiche générée !")
            st.image(output, caption="Clique droit pour enregistrer", use_column_width=True)
            with open(output, "rb") as file:
                st.download_button(
                    label="📥 Télécharger l’affiche",
                    data=file,
                    file_name="affiche_upm.png",
                    mime="image/png"
                )
            os.remove(output)
        except Exception as e:
            st.error(f"❌ Erreur : {e}")
    else:
        st.warning("Merci de remplir tous les champs.")
