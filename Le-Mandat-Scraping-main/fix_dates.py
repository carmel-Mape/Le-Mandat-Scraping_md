from pathlib import Path
import re

folder = Path("markdown_articles")
rfc3339_date = "2025-06-21T00:00:00Z"

for md_file in folder.glob("*.md"):
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.readlines()

    in_frontmatter = False
    date_found = False
    new_content = []

    for line in content:
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
            else:
                in_frontmatter = False
            new_content.append(line)
            continue

        if in_frontmatter and line.lower().startswith("date:"):
            # Remplace la ligne date par la date RFC3339 correcte
            new_content.append(f"date: {rfc3339_date}\n")
            date_found = True
        else:
            new_content.append(line)

    # Si date non trouvée dans le frontmatter, on l’ajoute juste après la première ligne '---'
    if not date_found:
        for i, line in enumerate(new_content):
            if line.strip() == "---":
                new_content.insert(i + 1, f"date: {rfc3339_date}\n")
                break

    # Réécriture du fichier
    with open(md_file, "w", encoding="utf-8") as f:
        f.writelines(new_content)

    print(f"✅ {md_file.name} corrigé")
