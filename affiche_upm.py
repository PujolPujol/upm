from newspaper import Article
from transformers import pipeline
from PIL import Image, ImageDraw, ImageFont

from trafilatura.metadata import extract_metadata
import textwrap
import trafilatura
import re




summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def get_summary_from_url(url):
    # 1. Télécharger le HTML brut
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        raise Exception("❌ Impossible de récupérer la page !")

    # 2. EXTRAIRE le texte principal
    text = trafilatura.extract(downloaded)
    if not text:
        raise Exception("❌ Texte vide après extraction.")

    # 3. EXTRAIRE le titre avec la métadonnée
   
    meta = extract_metadata(downloaded)

    title = meta.title if meta and meta.title else text.split("\n", 1)[0][:120]

    # 4. Résumé (facultatif mais tu le gardes)
    summary = summarizer(text[:1500],
                         max_length=150,
                         min_length=40,
                         do_sample=False)[0]["summary_text"]

    return title, summary






def create_affiche(title, summary, output="affiche.png"):
    # --- paramètres de mise en page ---
    W, H = 1080, 1350          # format portrait Instagram
    MARGIN = 60                # marge intérieure
    TITLE_SIZE = 54
    BODY_SIZE  = 36
    LINE_SPACING = 8           # espace entre lignes
    BG_COLOR = (255, 255, 255) # fond blanc

    # --- charger la police ---
    font_title = ImageFont.truetype("DejaVuSans.ttf", TITLE_SIZE)
    font_body  = ImageFont.truetype("DejaVuSans.ttf", BODY_SIZE)

    # --- canvas ---
    img  = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # --- préparer le titre (wrap + centrer) ---
    title_lines = textwrap.wrap(title, width=30)
    y = MARGIN
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=font_title)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text(((W - w) / 2, y), line, font=font_title, fill="black")
        y += h + LINE_SPACING

    # --- préparer le résumé ---
    max_body_height = H - MARGIN - 250  # place pour le logo
    body_lines = textwrap.wrap(summary, width=40)
    body_text = ""
    for line in body_lines:
        body_text += line + "\n"
        if (body_text.count("\n") + 1) * (BODY_SIZE + LINE_SPACING) > max_body_height:
            body_text += "…"
            break

    # mesurer le bloc de texte résumé
    bbox_body = draw.multiline_textbbox((0, 0), body_text, font=font_body, spacing=LINE_SPACING)
    w_body = bbox_body[2] - bbox_body[0]
    draw.multiline_text(((W - w_body) / 2, y + 20),
                        body_text,
                        font=font_body,
                        fill=(30, 30, 30),
                        align="center",
                        spacing=LINE_SPACING)

    # --- ajouter le logo ---
    try:
        logo = Image.open("logo_upm.png").convert("RGBA")
        logo_w = 160
        ratio  = logo_w / logo.width
        logo   = logo.resize((logo_w, int(logo.height * ratio)))
        logo_x = (W - logo.width) // 2
        logo_y = H - logo.height - MARGIN
        img.paste(logo, (logo_x, logo_y), logo)
    except FileNotFoundError:
        print("⚠️  Logo 'logo_upm.png' introuvable → affiche sans logo.")



# def create_affiche_style2(title, accroche, output="affiche2.png"):
#     W, H = 1080, 1350
#     BG_COLOR = (40, 40, 40)
#     FONT_ACC  = ("DejaVuSans.ttf", 46)
#     FONT_TITL = ("DejaVuSans.ttf", 56)
#     PAD_SIDE  = 90
#     PAD_BAND  = 28
#     TITLE_VPAD = 40

#     # Chargement fond
#     try:
#         bg = Image.open("background.png").resize((W, H))
#         img = bg.convert("RGB")
#     except:
#         img = Image.new("RGB", (W, H), BG_COLOR)

#     draw = ImageDraw.Draw(img)
#     font_acc  = ImageFont.truetype(*FONT_ACC)
#     font_titl = ImageFont.truetype(*FONT_TITL)

#     # --- Bandeau rouge ---
#     accroche = accroche.upper()
#     acc_lines = textwrap.wrap(accroche, width=35)
#     acc_line_h = font_acc.getbbox("Hg")[3]
#     band_h = 2*PAD_BAND + len(acc_lines)*acc_line_h + (len(acc_lines)-1)*6
#     draw.rectangle([(0, 0), (W, band_h)], fill=(220, 0, 32))

#     y = PAD_BAND
#     for line in acc_lines:
#         w_line = font_acc.getbbox(line)[2]
#         draw.text(((W - w_line)/2, y), line, font=font_acc, fill="white")
#         y += acc_line_h + 6

#     # --- Préparation texte du titre ---
#     title_lines = textwrap.wrap(f'« {title} »' , width=22)

#     line_h = font_titl.getbbox("Hg")[3]
#     total_title_h = len(title_lines)*line_h + (len(title_lines)-1)*18
#     bloc_height = total_title_h + 2*TITLE_VPAD

#     # --- Hauteur logo (même si on ne le charge pas maintenant) ---
#     logo_h = 200 + 40  # taille du logo + espace

#     # --- Centrage vertical du bloc noir ---
#     bloc_available = H - band_h - logo_h
#     bloc_y0 = band_h + (bloc_available - bloc_height) / 2
#     bloc_y1 = bloc_y0 + bloc_height
#     draw.rectangle([(PAD_SIDE, bloc_y0), (W - PAD_SIDE, bloc_y1)], fill="black")

#     # --- Écriture du titre centré dans le bloc ---
#     y_text = bloc_y0 + TITLE_VPAD
#     for line in title_lines:
#         w_line = font_titl.getbbox(line)[2]
#         draw.text(((W - w_line)/2, y_text), line, font=font_titl, fill="white")
#         y_text += line_h + 18

#     # --- Logo ---
#     try:
#         logo = Image.open("logo_upm.png").convert("RGBA")
#         logo = logo.resize((200, 200))
#         img.paste(logo, ((W - logo.width)//2, H - logo.height - 40), logo)
#     except:
#         print("⚠️  Logo introuvable")

#     img.save(output)
#     print(f"✅ Affiche centrée générée → {output}")





def create_affiche_style2(title, accroche, output="affiche2.png"):
    W, H = 1080, 1350
    BG_COLOR = (40, 40, 40)
    PAD_SIDE  = 90
    PAD_BAND  = 28
    TITLE_VPAD = 40

    FONT_ACC_BOLD = ("AgrandirTight-Bold.otf", 46)
    FONT_TITL = ("AgrandirTight.otf", 72)

    def wrap_text(text, font, max_width):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            bbox = font.getbbox(test_line)
            w = bbox[2] - bbox[0]
            if w <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    try:
        bg = Image.open("background.png").resize((W, H))
        img = bg.convert("RGB")
    except:
        img = Image.new("RGB", (W, H), BG_COLOR)

    draw = ImageDraw.Draw(img)

    font_acc  = ImageFont.truetype(*FONT_ACC_BOLD)
    font_titl = ImageFont.truetype(*FONT_TITL)

    # Accroche en majuscule et wrap dynamique
    accroche = accroche.upper()
    acc_lines = wrap_text(accroche, font_acc, W - 2 * PAD_SIDE)
    acc_line_h = font_acc.getbbox("Hg")[3]
    band_h = 2 * PAD_BAND + len(acc_lines) * acc_line_h + (len(acc_lines) - 1) * 6
    draw.rectangle([(0, 0), (W, band_h)], fill=(220, 0, 32))

    y = PAD_BAND
    for line in acc_lines:
        w_line = font_acc.getbbox(line)[2]
        draw.text(((W - w_line) / 2, y), line, font=font_acc, fill="white")
        y += acc_line_h + 6

    # Nettoyage titre et gestion ponctuation finale
    title_clean = re.sub(r'[«»"“”„‟‟‘’]', '', title).strip()

    def is_punctuation_only(s):
        return all(c in "?!.:;," for c in s)

    words = title_clean.split()

    if not words:
        final_title = f'« {title_clean} »'
    else:
        if is_punctuation_only(words[-1]) and len(words) >= 2:
            # On met un espace entre les deux derniers mots (mot + ponctuation)
            last_words = words[-2] + " " + words[-1]
            title_main = " ".join(words[:-2])
        else:
            last_words = words[-1]
            title_main = " ".join(words[:-1])

        if title_main:
            final_title = f'« {title_main} {last_words}\u00A0»'
        else:
            final_title = f'« {last_words}\u00A0»'

    max_text_width = W - 2 * PAD_SIDE
    title_lines = wrap_text(final_title, font_titl, max_text_width)
    line_h = font_titl.getbbox("Hg")[3]
    total_title_h = len(title_lines) * line_h + (len(title_lines) - 1) * 18
    bloc_height = total_title_h + 2 * TITLE_VPAD

    logo_h = 200 + 40

    bloc_available = H - band_h - logo_h
    bloc_y0 = band_h + (bloc_available - bloc_height) / 2
    bloc_y1 = bloc_y0 + bloc_height
    draw.rectangle([(PAD_SIDE, bloc_y0), (W - PAD_SIDE, bloc_y1)], fill="black")

    y_text = bloc_y0 + TITLE_VPAD
    for line in title_lines:
        w_line = font_titl.getbbox(line)[2]
        draw.text(((W - w_line) / 2, y_text), line, font=font_titl, fill="white")
        y_text += line_h + 18

    try:
        logo = Image.open("logo_upm.png").convert("RGBA")
        logo = logo.resize((200, 200))
        img.paste(logo, ((W - logo.width) // 2, H - logo.height - 40), logo)
    except:
        print("⚠️  Logo introuvable")

    img.save(output)
    print(f"✅ Affiche centrée générée → {output}")

    
if __name__ == "__main__":
    url = input("URL de l'article : ")
    accroche = input("Phrase d'accroche : ")
    title, _ = get_summary_from_url(url)   # on n’affiche plus le résumé
    create_affiche_style2(title, accroche)



