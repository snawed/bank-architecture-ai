from jira import JIRA
from shared.config.config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN

jira = JIRA(server=JIRA_URL, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))

def get_issue(issue_key):
    return jira.issue(issue_key)

def extract_domain(summary):
    summary = summary.lower()

    if "customeronboarding" in summary:
        return "CustomerOnboarding"
    elif "payments" in summary:
        return "Payments"
    elif "cards" in summary:
        return "Cards"
    else:
        raise Exception("Domain not found")

def attach_file(issue, file_path):
    jira.add_attachment(issue=issue, attachment=file_path)
    print("✅ Attached to Jira")