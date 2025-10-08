import requests
import json
import os, json, argparse
from dotenv import load_dotenv
from normalize_data import normalize_changelog_metadata

load_dotenv()
token = os.getenv("API_TOKEN_JIRA")
base_url = os.getenv("BASE_URL_JIRA")
email = os.getenv("USER_EMAIL_JIRA")
auth = (email, token)

sprint_data_path = "../data/bronze/sprints.json"
issues_data_path = "../data/bronze/issues.json"
changelogs_data_path = "../data/bronze/changelogs.json"

def getSprints(board_id, limit=5):
    url = f"{base_url}/rest/agile/1.0/board/{board_id}/sprint" 
    resp = requests.get(url, auth=auth) 
    resp.raise_for_status() 
    sprints = resp.json().get("values", [])

    # Sort by endDate descending, get most recent ones
    sprints = sorted(sprints, key=lambda x: x.get("endDate", ""), reverse=True)[:limit]
    sprint_dict = {s["name"]: s for s in sprints}

    try:
        with open(sprint_data_path, "w") as f:
            json.dump(sprint_dict, f, indent=4)
            print(f"Saved {len(sprint_dict)} sprints to sprints.json")
    except IOError as e:
        print(f"Error saving sprint data: {e}")

def getIssuesBySprints(sprint_names): 
    with open(sprint_data_path, "r") as f:
        sprints = json.load(f)

    all_issues = {}

    for sprint_name in sprint_names:
        sprint_id = sprints[sprint_name]["id"]
        url = f"{base_url}/rest/agile/1.0/sprint/{sprint_id}/issue"
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        issues = resp.json().get("issues", [])
        for issue in issues:
            all_issues[issue["key"]] = issue

    try:
        with open(issues_data_path, "w") as f:
            json.dump(all_issues, f, indent=4)
            print(f"Saved {len(all_issues)} issues to issues.json")
    except IOError as e:
        print(f"Error saving issues: {e}")

def getChangelogsForIssues(issue_keys): 
    all_changelogs = {}

    for issue_key in issue_keys:
        url = f"{base_url}/rest/api/3/issue/{issue_key}?expand=changelog"
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        data = resp.json()
        changelog = data.get("changelog", {}).get("histories", [])

        normalized_rows = normalize_changelog_metadata(issue_key, changelog)
        all_changelogs[issue_key] = {
            "issue": issue_key,
            "transitions": normalized_rows
        }

    try:
        with open(changelogs_data_path, "w") as f:
            json.dump(all_changelogs, f, indent=4)
            print(f"Saved changelogs for {len(all_changelogs)} issues to changelogs.json")
    except IOError as e:
        print(f"Error saving changelogs: {e}")

# def createSubTask(issue_key, subtask_packet): TODO
# def createBacklogClone(issue_key) : TODO



# test code 
getSprints(34)
getIssuesBySprints(["sprint_1_october25"])
getChangelogsForIssues(["TB-1", "TB-2"])
