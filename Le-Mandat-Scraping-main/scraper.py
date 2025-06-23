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
DELAY = 2  # secondes entre les pages

CONTRIBUTOR_ID = 61825
AUTHOR = "Le Mandat"
SOURCE = "mandat_scraper"

articles_data = []

def get_category_links():
    url = f"{BASE_URL}/kir/amakuru/"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print("⚠️ Impossible d'accéder à la page des catégories.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    category_links = []

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if "/kir/blog/category/" in href:
            full_url = href if href.startswith("http") else f"{BASE_URL}{href}"
            if full_url not in category_links:
                category_links.append(full_url)

    return category_links

def extract_category_name(url):
    """
    Extrait le nom brut de la catégorie depuis l’URL.
    Exemple: https://.../category/politique/ => politique
    """
    parts = url.strip("/").split("/")
    if "category" in parts:
        index = parts.index("category")
        if index + 1 < len(parts):
            return parts[index + 1]
    return "autre"

def scrape_category(category_url):
    page = 1
    category_name = extract_category_name(category_url)

    while True:
        print(f"\n🔎 Page {page} de la catégorie: {category_name}")
        try:
            url = f"{category_url}page/{page}/"
            response = requests.get(url, headers=HEADERS)

            if response.status_code != 200:
                print("⚠️ Fin ou erreur.")
                break

            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.find_all("article")
            if not articles:
                print("✅ Fin du scraping : plus d'articles.")
                break

            for article in articles:
                try:
                    header = article.find(["h2", "h3"])
                    if not header:
                        continue
                    titre = header.get_text(strip=True)

                    lien_tag = article.find("a", href=True)
                    if not lien_tag:
                        continue
                    lien = lien_tag["href"]

                    print(f"📰 {titre}")

                    article_res = requests.get(lien, headers=HEADERS)
                    if article_res.status_code != 200:
                        continue

                    article_soup = BeautifulSoup(article_res.text, "html.parser")
                    content_div = article_soup.find("div", class_="entry-content")
                    if not content_div:
                        continue

                    if content_div.find("iframe") or content_div.find("video"):
                        print("🎬 Ignoré (vidéo).")
                        continue

                    paragraphs = content_div.find_all("p")
                    contenu = ""
                    for p in paragraphs:
                        texte = p.get_text(strip=True)
                        if texte:
                            contenu += texte + "\n"

                    mots_kirundi = ["n'", "mu", "ku", "na", "ya", "ni", "iyo", "bar", "abo", "y’"]
                    if any(mot in contenu.lower() for mot in mots_kirundi):
                        article_info = {
                            "contributor_id": CONTRIBUTOR_ID,
                            "title": titre,
                            "author": AUTHOR,
                            "source": SOURCE,
                            "data": contenu.strip(),
                            "category": category_name,
                            "lien": lien  # Utile pour créer le lien dans le .md
                        }
                        articles_data.append(article_info)
                    else:
                        print("🔕 Ignoré (non Kirundi).")

                except Exception as e:
                    print(f"🚫 Erreur sur un article : {e}")

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

    # Sauvegarde finale
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(articles_data, f, ensure_ascii=False, indent=4)

    print(f"\n✅ {len(articles_data)} article(s) sauvegardé(s) dans '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()
