import os
import requests
import yaml
from pathlib import Path
from datetime import datetime

# ⚠️ IMPORTANT: Remplacez par l'URL de votre prof
UPLOAD_URL = os.getenv('UPLOAD_URL', 'http://172.233.123.71:8080/api/upload')  # À adapter

def upload_article_content(file_path: Path, article: dict):
    """
    Upload un article en suivant exactement la logique du prof
    """
    contributor_id = 61825

    raw_date = article.get('date', '2025-01-01')
    try:
        # Si déjà au bon format, rien ne change
        parsed_date = datetime.fromisoformat(raw_date).isoformat() + "Z"
    except Exception:
        parsed_date = "2025-01-01T00:00:00Z"
    
    # Construction du form_data exactement comme le prof
    form_data = {
        'contributor_id': contributor_id, 
        'title': article['title'],
        'author': article.get('author', ''),
        'source': article.get('url', ''),  # Le prof utilise 'source' pour l'URL
        'date': parsed_date,
        'category': article.get('category', ''),
    }
    
    # Lecture du contenu du fichier (comme le prof)
    with open(file_path, 'rb') as f:
        files = {
            'file': (file_path.name, f, 'text/markdown')
        }
        
        try:
            response = requests.post(UPLOAD_URL, data=form_data, files=files)
            
            # Gestion des réponses comme le prof
            if response.status_code == 201:
                print(f"✅ Successfully uploaded article: {article['title']}")
                return True
            elif response.status_code == 208:
                print(f"⚠️ Article already uploaded: {article['title']}")
                return False
            else:
                print(f"❌ Failed to upload article: {article['title']}")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"🚨 Network error for {article['title']}: {e}")
            return False

def main():
    """
    Script principal adapté à la logique du prof
    """
    folder = "Markdown_articles"
    
    # Vérification que le dossier existe
    if not os.path.exists(folder):
        print(f"❌ Le dossier '{folder}' n'existe pas. Exécutez d'abord generate_md.py")
        return
    
    # Liste des fichiers markdown
    files = [f for f in os.listdir(folder) if f.endswith(".md")]
    print(f"📦 {len(files)} fichiers trouvés dans '{folder}'.")
    
    if not files:
        print("⚠️ Aucun fichier .md trouvé!")
        return
    
    # Variables de suivi
    uploaded_count = 0
    already_exists_count = 0
    failed_count = 0
    
    # Traitement de chaque fichier
    for filename in files:
        filepath = Path(folder) / filename
        
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
            
            # Extraction du front matter YAML
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    yaml_raw = parts[1]
                    markdown_body = parts[2]
                    
                    try:
                        # Parse des métadonnées YAML
                        metadata = yaml.safe_load(yaml_raw)
                        
                        # Validation des champs requis
                        if not metadata.get('title'):
                            print(f"⚠️ Titre manquant dans {filename}")
                            failed_count += 1
                            continue
                        
                        # Upload de l'article
                        result = upload_article_content(filepath, metadata)
                        
                        if result:
                            uploaded_count += 1
                        else:
                            # Vérifier si c'est un doublon (status 208) ou une vraie erreur
                            already_exists_count += 1
                            
                    except yaml.YAMLError as e:
                        print(f"❌ Erreur YAML dans {filename}: {e}")
                        failed_count += 1
                else:
                    print(f"⚠️ Métadonnées incomplètes dans {filename}")
                    failed_count += 1
            else:
                print(f"⚠️ Pas de front matter YAML trouvé dans {filename}")
                failed_count += 1
                
        except Exception as e:
            print(f"❌ Erreur lors du traitement de {filename}: {e}")
            failed_count += 1
    
    # Résumé final
    print(f"\n📊 RÉSUMÉ:")
    print(f"   ✅ Uploadés avec succès: {uploaded_count}")
    print(f"   ⚠️ Déjà existants: {already_exists_count}")
    print(f"   ❌ Échecs: {failed_count}")
    print(f"   📦 Total traité: {len(files)}")

if __name__ == "__main__":
    # Vérification des variables d'environnement
    if not os.getenv('UPLOAD_URL'):
        print("⚠️ ATTENTION: Variable UPLOAD_URL non définie!")
        print("   Utilisez: export UPLOAD_URL='http://votre-serveur.com/upload'")
        print("   Ou modifiez directement le code avec l'URL de votre prof")
        print()
    
    if not os.getenv('CONTRIBUTOR_ID'):
        print("⚠️ ATTENTION: Variable CONTRIBUTOR_ID non définie!")
        print("   Utilisez: export CONTRIBUTOR_ID='votre_id'")
        print("   Sinon '00000' sera utilisé par défaut")
        print()
    
    main()
