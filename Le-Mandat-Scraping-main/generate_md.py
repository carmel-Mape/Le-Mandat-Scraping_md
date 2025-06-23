import os
import json
import hashlib
from datetime import datetime

# Chargement des articles
with open("articles_kirundi.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

# Dossier de sortie
output_dir = "Markdown_articles"
os.makedirs(output_dir, exist_ok=True)

def nettoyer_nom_fichier(texte):
    """Génère un nom de fichier unique et propre"""
    hash_id = hashlib.sha1(texte.encode("utf-8")).hexdigest()[:8]
    texte = texte.lower().replace(" ", "-").replace("'", "").replace("'", "").replace(":", "").replace("?", "")
    return f"mandat_scraper__{texte[:30]}-{hash_id}.md"

def format_date_iso(date_str):
    """Formatte la date au format YYYY-MM-DD pour le prof"""
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return d.strftime("%Y-%m-%d")
    except:
        return "2025-01-01"  # date par défaut

# Génération des fichiers .md adaptés à la logique du prof
for article in articles:
    try:
        titre = article.get("title", "Sans titre")
        contenu = article.get("data", "").strip()
        auteur = article.get("author", "Le Mandat")
        
        # ⚠️ IMPORTANT: Le prof utilise 'url' pour la source et 'postedAt' pour la date
        # On adapte nos champs aux attentes de son code
        url_source = article.get("lien", "")  # Notre 'lien' devient 'url'
        category = article.get("category", "inconnue")
        contributor_id = article.get("contributor_id", "00000")
        date_article = format_date_iso(article.get("date", "2025-01-01"))
        
        nom_fichier = nettoyer_nom_fichier(titre)
        chemin_fichier = os.path.join(output_dir, nom_fichier)
        
        # Front matter YAML adapté aux champs que le prof attend
        # Le prof utilise: contributor_id, title, author, url, postedAt, category
        contenu_md = f"""---
contributor_id: "{contributor_id}"
title: "{titre}"
author: "{auteur}"
url: "{url_source}"
postedAt: "{date_article}"
category: "{category}"
---

{contenu}
"""
        
        with open(chemin_fichier, "w", encoding="utf-8") as f:
            f.write(contenu_md)
        
        print(f"✅ Fichier généré : {nom_fichier}")
    except Exception as e:
        print(f"❌ Erreur lors de la génération de {titre}: {e}")

print(f"\n🎯 Fichiers générés dans '{output_dir}' avec les champs attendus par le prof:")
print("- contributor_id, title, author, url, postedAt, category")