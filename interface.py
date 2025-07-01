import gradio as gr
from affiche_upm import get_summary_from_url, create_affiche_style2
import uuid
import os

def generate_affiche(url, accroche):
    try:
        title, _ = get_summary_from_url(url)
        filename = f"affiche_{uuid.uuid4().hex[:8]}.png"
        create_affiche_style2(title, accroche, output=filename)
        return filename
    except Exception as e:
        return f"❌ Erreur : {str(e)}"

demo = gr.Interface(
    fn=generate_affiche,
    inputs=[
        gr.Textbox(label="URL de l'article", placeholder="https://..."),
        gr.Textbox(label="Phrase d'accroche", placeholder="LISEZ L'ARTICLE DU MONDE")
    ],
    outputs=gr.Image(type="filepath", label="Affiche générée"),
    title="📰 Générateur d'affiches UPM",
    description="Collez l'URL d’un article + une phrase d'accroche, et téléchargez une affiche prête à publier."
)

if __name__ == "__main__":
    demo.launch()
