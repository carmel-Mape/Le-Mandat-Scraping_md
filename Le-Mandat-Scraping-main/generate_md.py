import os
import json
import re
import hashlib

# Créer le dossier de destination
os.makedirs("data/articles", exist_ok=True)

# Charger les articles
with open("articles_kirundi.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

for art in articles:
    title = art.get("title", "").strip() or "Sans titre"
    lien = art.get("lien", "")
    contenu = art.get("contenu", "")

    # Générer un nom de fichier unique basé sur le lien
    hash_id = hashlib.md5(lien.encode()).hexdigest()[:8]  # 8 caractères du hash
    safe_title = re.sub(r"[^\w\s-]", "", title).strip().lower()
    safe_title = re.sub(r"\s+", "-", safe_title)

    prefix = "mandat_scraper"
    filename = f"{prefix}__{safe_title}-{hash_id}.md"
    path = os.path.join("data/articles", filename)

    with open(path, "w", encoding="utf-8") as f_out:
        f_out.write(f"# {title}\n\n")
        f_out.write(f"[Lire l’article original]({lien})\n\n")
        f_out.write(contenu)

    print(f"✅ Fichier généré : {filename}")
