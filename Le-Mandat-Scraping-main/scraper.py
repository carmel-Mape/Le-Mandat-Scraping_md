import requests
from bs4 import BeautifulSoup
import json
import time

# Configuration
BASE_URL = "https://lemandat.org"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
OUTPUT_FILE = "articles_kirundi.json"
DELAY = 2  # secondes entre chaque page

articles_data = []

def get_category_links():
    """
    Récupère les liens de toutes les catégories sous la section AMAKURU.
    """
    url = f"{BASE_URL}/kir/amakuru/"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print("⚠️ Impossible d'accéder à la page principale des catégories.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    category_links = []

    # Rechercher les liens de catégories dans le menu ou la page
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if "/kir/blog/category/" in href:
            full_url = href if href.startswith("http") else f"{BASE_URL}{href}"
            if full_url not in category_links:
                category_links.append(full_url)

    return category_links

def scrape_category(category_url):
    """
    Scrape tous les articles textuels d'une catégorie donnée.
    """
    page = 1
    while True:
        print(f"\n🔎 Traitement de la page {page} de la catégorie: {category_url}")
        try:
            url = f"{category_url}page/{page}/"
            response = requests.get(url, headers=HEADERS)

            if response.status_code != 200:
                print("⚠️ Page non trouvée ou erreur de connexion.")
                break

            soup = BeautifulSoup(response.text, "html.parser")

            # Trouver tous les articles
            articles = soup.find_all("article")
            if not articles:
                print("✅ Fin du scraping : plus d'articles trouvés.")
                break

            for article in articles:
                try:
                    # Extraire le titre
                    header = article.find(["h2", "h3"])
                    if header:
                        titre = header.get_text(strip=True)
                    else:
                        continue

                    # Extraire le lien
                    lien_tag = article.find("a", href=True)
                    if lien_tag:
                        lien = lien_tag["href"]
                    else:
                        continue

                    print(f"📰 Article : {titre}")

                    # Aller chercher le contenu complet de l'article
                    article_res = requests.get(lien, headers=HEADERS)
                    if article_res.status_code != 200:
                        print("⛔ Erreur lors du chargement de l'article.")
                        continue

                    article_soup = BeautifulSoup(article_res.text, "html.parser")
                    content_div = article_soup.find("div", class_="entry-content")
                    if not content_div:
                        print("❌ Contenu introuvable.")
                        continue

                    # Vérifier s'il y a une vidéo dans le contenu
                    if content_div.find("iframe") or content_div.find("video"):
                        print("🎬 Article ignoré (contient une vidéo).")
                        continue

                    # Extraire tous les paragraphes de l'article
                    paragraphs = content_div.find_all("p")
                    contenu = ""
                    for p in paragraphs:
                        texte = p.get_text(strip=True)
                        if texte:
                            contenu += texte + "\n"

                    # Filtrage basique pour s'assurer que c’est du Kirundi
                    mots_kirundi = ["n'", "mu", "ku", "na", "ya", "ni", "iyo", "bar", "abo", "y’"]
                    if any(mot in contenu.lower() for mot in mots_kirundi):
                        article_info = {
                            "titre": titre,
                            "lien": lien,
                            "contenu": contenu.strip()
                        }
                        articles_data.append(article_info)
                    else:
                        print("🔕 Article ignoré (probablement pas en Kirundi).")

                except Exception as e:
                    print(f"🚫 Erreur lors du traitement d’un article : {e}")

            time.sleep(DELAY)
            page += 1

        except Exception as e:
            print(f"🚨 Erreur critique : {e}")
            break

def main():
    category_links = get_category_links()
    if not category_links:
        print("❌ Aucune catégorie trouvée.")
        return

    for category_url in category_links:
        scrape_category(category_url)

    # Sauvegarder les articles dans un fichier JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(articles_data, f, ensure_ascii=False, indent=4)

    print(f"\n✅ Scraping terminé. {len(articles_data)} article(s) sauvegardé(s) dans '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()
