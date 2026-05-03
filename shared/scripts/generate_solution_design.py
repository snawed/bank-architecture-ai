import sys
from datetime import date
from pathlib import Path


def main():
    if len(sys.argv) not in [2, 3]:
        raise SystemExit("Usage: python shared/scripts/generate_solution_design.py <domain> [issue_key]")

    domain = sys.argv[1]
    issue_key = sys.argv[2] if len(sys.argv) == 3 else "TBD"

    domain_dir = Path(domain)
    context_path = domain_dir / "docs" / "context.md"
    template_path = Path("shared/templates/solution_design_template.md")
    output_path = domain_dir / "docs" / "solution_design.md"

    if not context_path.exists():
        raise SystemExit(f"Context file not found: {context_path}")

    if not template_path.exists():
        raise SystemExit(f"Template file not found: {template_path}")

    context = context_path.read_text(encoding="utf-8").strip()
    template = template_path.read_text(encoding="utf-8")

    replacements = {
        "{{DOMAIN}}": domain,
        "{{ISSUE_KEY}}": issue_key,
        "{{UPDATED_DATE}}": date.today().isoformat(),
        "{{EXECUTIVE_SUMMARY}}": build_executive_summary(domain, context),
        "{{BUSINESS_CONTEXT}}": context,
    }

    document = template
    for placeholder, value in replacements.items():
        document = document.replace(placeholder, value)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding="utf-8")

    print(f"✅ Solution design generated: {output_path}")


def build_executive_summary(domain, context):
    first_lines = [
        line.strip()
        for line in context.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    summary_basis = " ".join(first_lines[:3])

    if not summary_basis:
        summary_basis = "The design is based on the provided domain context."

    return (
        f"This document describes the target solution design for {domain}. "
        f"It uses the shared architecture template and includes C1-C4 diagrams, "
        f"functional design, technical design, security, compliance, operations, "
        f"risks, and approval sections. {summary_basis}"
    )


if __name__ == "__main__":
    main()
