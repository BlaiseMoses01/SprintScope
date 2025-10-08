from datetime import datetime
import pandas as pd

def normalize_changelog_metadata(issue_key, changelog):
    rows = []
    for entry in changelog:
        created = entry.get("created")
        author = entry.get("author", {}).get("displayName", "Unknown")

        for item in entry.get("items", []):
            if item["field"] == "status":
                rows.append({
                    "issue": issue_key,
                    "changed_at": created,
                    "author": author,
                    "from_status": item.get("fromString"),
                    "to_status": item.get("toString")
                })
    return rows