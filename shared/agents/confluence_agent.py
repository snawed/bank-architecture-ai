import requests
from html import escape
from pathlib import Path
from requests.auth import HTTPBasicAuth
from shared.config.config import CONFLUENCE_URL, JIRA_EMAIL, JIRA_API_TOKEN

def upload_file(file_path, page_id):
    file_name = Path(file_path).name
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {
        "X-Atlassian-Token": "no-check"
    }

    existing_attachment = get_attachment(page_id, file_name, auth)

    if existing_attachment:
        attachment_id = existing_attachment["id"]
        url = f"{CONFLUENCE_URL}/rest/api/content/{page_id}/child/attachment/{attachment_id}/data"
        success_message = "✅ Updated Confluence attachment"
    else:
        url = f"{CONFLUENCE_URL}/rest/api/content/{page_id}/child/attachment"
        success_message = "✅ Uploaded to Confluence"

    with open(file_path, 'rb') as f:
        files = {'file': f}

        response = requests.post(
            url,
            headers=headers,
            auth=auth,
            files=files
        )

    if response.status_code in [200, 201]:
        print(success_message)
    else:
        raise Exception(f"Confluence upload failed: {response.text}")

def get_attachment(page_id, file_name, auth):
    response = requests.get(
        f"{CONFLUENCE_URL}/rest/api/content/{page_id}/child/attachment",
        auth=auth,
        params={"filename": file_name}
    )

    response.raise_for_status()

    results = response.json().get("results", [])

    if not results:
        return None

    return results[0]

def update_page_content(page_id, title, storage_body):
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    page = get_page(page_id, auth)

    url = f"{CONFLUENCE_URL}/rest/api/content/{page_id}"
    payload = {
        "id": page_id,
        "type": page.get("type", "page"),
        "title": title or page["title"],
        "version": {
            "number": page["version"]["number"] + 1
        },
        "body": {
            "storage": {
                "value": storage_body,
                "representation": "storage"
            }
        }
    }

    response = requests.put(url, auth=auth, json=payload)
    response.raise_for_status()
    print("✅ Updated Confluence page content")

def get_page(page_id, auth):
    response = requests.get(
        f"{CONFLUENCE_URL}/rest/api/content/{page_id}",
        auth=auth,
        params={"expand": "version,title,type"}
    )
    response.raise_for_status()
    return response.json()

def render_solution_design_storage(domain, solution_design_path, diagram_names):
    markdown = Path(solution_design_path).read_text(encoding="utf-8")
    body = markdown_to_storage(markdown)
    diagram_gallery = render_diagram_gallery(diagram_names)
    return f"{diagram_gallery}{body}"

def render_diagram_gallery(diagram_names):
    parts = ["<h1>Architecture Diagrams</h1>"]

    for diagram_name in diagram_names:
        parts.append(f"<h2>{escape(diagram_name.replace('.svg', ''))}</h2>")
        parts.append(render_attachment_image(diagram_name))

    return "\n".join(parts)

def markdown_to_storage(markdown):
    lines = markdown.splitlines()
    html_parts = []
    list_items = []
    table_rows = []
    code_lines = []
    in_code_block = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code_block:
                html_parts.append(render_code_block(code_lines))
                code_lines = []
                in_code_block = False
            else:
                flush_list(html_parts, list_items)
                flush_table(html_parts, table_rows)
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if not stripped:
            flush_list(html_parts, list_items)
            flush_table(html_parts, table_rows)
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            flush_list(html_parts, list_items)
            table_rows.append(stripped)
            continue

        flush_table(html_parts, table_rows)

        if stripped.startswith("- "):
            list_items.append(stripped[2:])
            continue

        flush_list(html_parts, list_items)

        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            text = stripped[level:].strip()
            level = min(level, 6)
            html_parts.append(f"<h{level}>{escape(text)}</h{level}>")
        elif stripped.startswith("![") and "](" in stripped:
            file_name = Path(stripped.split("](", 1)[1].rstrip(")")).name
            html_parts.append(render_attachment_image(file_name))
        else:
            html_parts.append(f"<p>{escape(stripped)}</p>")

    flush_list(html_parts, list_items)
    flush_table(html_parts, table_rows)

    if code_lines:
        html_parts.append(render_code_block(code_lines))

    return "\n".join(html_parts)

def flush_list(html_parts, list_items):
    if not list_items:
        return

    items = "".join(f"<li>{escape(item)}</li>" for item in list_items)
    html_parts.append(f"<ul>{items}</ul>")
    list_items.clear()

def flush_table(html_parts, table_rows):
    if not table_rows:
        return

    rows = []
    for index, row in enumerate(table_rows):
        cells = [cell.strip() for cell in row.strip("|").split("|")]

        if index == 1 and all(set(cell) <= {"-", ":"} for cell in cells):
            continue

        tag = "th" if index == 0 else "td"
        rendered_cells = "".join(f"<{tag}>{escape(cell)}</{tag}>" for cell in cells)
        rows.append(f"<tr>{rendered_cells}</tr>")

    html_parts.append(f"<table><tbody>{''.join(rows)}</tbody></table>")
    table_rows.clear()

def render_code_block(code_lines):
    code = "\n".join(code_lines)
    return (
        '<ac:structured-macro ac:name="code">'
        f"<ac:plain-text-body><![CDATA[{code}]]></ac:plain-text-body>"
        "</ac:structured-macro>"
    )

def render_attachment_image(file_name):
    return (
        "<ac:image>"
        f'<ri:attachment ri:filename="{escape(file_name)}" />'
        "</ac:image>"
    )
