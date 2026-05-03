from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs


HOST = "127.0.0.1"
PORT = 8000


class ArchitectureUIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.render_page()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        form = parse_qs(body)

        issue_key = get_form_value(form, "issue_key")
        domain = get_form_value(form, "domain")
        action = get_form_value(form, "action")

        try:
            message, resolved_domain = run_action(action, issue_key, domain)
            self.render_page(
                issue_key=issue_key,
                domain=resolved_domain or domain,
                message=message,
                is_error=False,
            )
        except Exception as exc:
            self.render_page(
                issue_key=issue_key,
                domain=domain,
                message=str(exc),
                is_error=True,
            )

    def render_page(self, issue_key="", domain="", message="", is_error=False):
        html = render_html(issue_key, domain, message, is_error)
        encoded = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format, *args):
        return


def get_form_value(form, key):
    values = form.get(key, [""])
    return values[0].strip()


def run_action(action, issue_key, domain):
    from shared.agents.jira_agent import extract_domain, get_issue

    if action == "resolve_domain":
        issue = get_issue(issue_key)
        resolved_domain = extract_domain(issue.fields.summary)
        return f"Resolved {issue.key}: {issue.fields.summary}", resolved_domain

    if action == "generate_package":
        from shared.agents.architecture_agent import run_all_diagrams
        from shared.agents.design_document_agent import generate_solution_design
        from shared.agents.peer_review_agent import generate_peer_review

        issue = get_issue(issue_key)
        resolved_domain = domain or extract_domain(issue.fields.summary)
        run_all_diagrams(resolved_domain)
        generate_solution_design(resolved_domain, issue.key)
        generate_peer_review(resolved_domain, issue.key)
        return f"Generated solution design package and peer review for {issue.key} / {resolved_domain}.", resolved_domain

    if action == "peer_review":
        from shared.agents.peer_review_agent import generate_peer_review

        issue = get_issue(issue_key)
        resolved_domain = domain or extract_domain(issue.fields.summary)
        generate_peer_review(resolved_domain, issue.key)
        return f"Generated peer review for {issue.key} / {resolved_domain}.", resolved_domain

    if action == "create_pr":
        from shared.agents.github_agent import create_branch, commit_changes, create_pr, push_branch

        issue = get_issue(issue_key)
        resolved_domain = domain or extract_domain(issue.fields.summary)
        branch_name = f"{resolved_domain.lower()}-solution-design-{issue.key.lower()}"
        create_branch(branch_name)
        commit_changes(f"{issue.key}: AI generated solution design package")
        push_branch(branch_name)
        pr_url = create_pr(
            f"{issue.key} - {resolved_domain} Solution Design",
            (
                "AI generated solution design with C1-C4 diagrams and peer review.\n\n"
                "Responsible architect owns resolution of peer review and human reviewer comments before publication."
            ),
            branch_name,
        )
        return f"Created PR: {pr_url}", resolved_domain

    if action == "publish":
        from shared.agents.publish_agent import publish

        issue = get_issue(issue_key)
        resolved_domain = domain or extract_domain(issue.fields.summary)
        publish(issue, resolved_domain)
        return f"Published solution design and diagrams for {issue.key} / {resolved_domain}.", resolved_domain

    raise ValueError("Unknown action")


def render_html(issue_key, domain, message, is_error):
    status_class = "error" if is_error else "success"
    status_html = f'<div class="status {status_class}">{escape_html(message)}</div>' if message else ""
    artifacts = render_artifact_links(domain)

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Architecture Workflow Console</title>
  <style>
    body {{
      margin: 0;
      font-family: Arial, sans-serif;
      background: #f5f7fa;
      color: #172033;
    }}
    header {{
      background: #172033;
      color: white;
      padding: 18px 28px;
    }}
    main {{
      max-width: 980px;
      margin: 28px auto;
      padding: 0 20px;
    }}
    section {{
      background: white;
      border: 1px solid #d9e0ea;
      border-radius: 6px;
      padding: 20px;
      margin-bottom: 18px;
    }}
    label {{
      display: block;
      font-weight: 700;
      margin: 12px 0 6px;
    }}
    input {{
      width: 100%;
      box-sizing: border-box;
      padding: 10px;
      border: 1px solid #aeb8c5;
      border-radius: 4px;
      font-size: 14px;
    }}
    .buttons {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 18px;
    }}
    button {{
      border: 0;
      border-radius: 4px;
      padding: 10px 14px;
      background: #2454a6;
      color: white;
      font-weight: 700;
      cursor: pointer;
    }}
    button.secondary {{
      background: #52606d;
    }}
    button.warning {{
      background: #9a5b00;
    }}
    .status {{
      border-radius: 4px;
      padding: 12px;
      margin-bottom: 16px;
      white-space: pre-wrap;
    }}
    .success {{
      background: #e7f6ed;
      border: 1px solid #8cc9a1;
    }}
    .error {{
      background: #fdecea;
      border: 1px solid #e2a19a;
    }}
    code {{
      background: #eef2f7;
      padding: 2px 4px;
      border-radius: 3px;
    }}
    ul {{
      line-height: 1.7;
    }}
  </style>
</head>
<body>
  <header>
    <h1>Architecture Workflow Console</h1>
  </header>
  <main>
    {status_html}
    <section>
      <h2>Run Workflow</h2>
      <form method="post">
        <label for="issue_key">Jira Issue Key</label>
        <input id="issue_key" name="issue_key" value="{escape_html(issue_key)}" placeholder="ARCG-1">

        <label for="domain">Domain</label>
        <input id="domain" name="domain" value="{escape_html(domain)}" placeholder="CustomerOnboarding">

        <div class="buttons">
          <button name="action" value="resolve_domain" class="secondary">Resolve Domain</button>
          <button name="action" value="generate_package">Generate Design Package</button>
          <button name="action" value="peer_review">Run Peer Review</button>
          <button name="action" value="create_pr">Create PR</button>
          <button name="action" value="publish" class="warning">Publish</button>
        </div>
      </form>
    </section>

    <section>
      <h2>Recommended Flow</h2>
      <ol>
        <li>Resolve domain from Jira.</li>
        <li>Generate design package: C1-C4, solution design, peer review.</li>
        <li>Create PR for human review.</li>
        <li>Responsible architect resolves PR comments.</li>
        <li>Publish only after approval.</li>
      </ol>
    </section>

    <section>
      <h2>Local Artefacts</h2>
      {artifacts}
    </section>
  </main>
</body>
</html>"""


def render_artifact_links(domain):
    if not domain:
        return "<p>Enter or resolve a domain to see expected artefacts.</p>"

    paths = [
        f"{domain}/docs/solution_design.md",
        f"{domain}/reviews/peer_review_ARCG-1.md",
        f"{domain}/diagrams/C1.svg",
        f"{domain}/diagrams/C2.svg",
        f"{domain}/diagrams/C3.svg",
        f"{domain}/diagrams/C4.svg",
    ]

    items = []
    for path in paths:
        exists = "exists" if Path(path).exists() else "missing"
        items.append(f"<li><code>{escape_html(path)}</code> - {exists}</li>")

    return "<ul>" + "".join(items) + "</ul>"


def escape_html(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def main():
    server = HTTPServer((HOST, PORT), ArchitectureUIHandler)
    print(f"Architecture Workflow Console running at http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
