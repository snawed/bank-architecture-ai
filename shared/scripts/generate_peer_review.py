import sys
from datetime import date
from pathlib import Path


POLICY_FILES = [
    "shared/policies/security_review_checklist.md",
    "shared/policies/data_review_checklist.md",
    "shared/policies/integration_review_checklist.md",
    "shared/policies/nfr_review_checklist.md",
    "shared/policies/regulatory_review_checklist.md",
]


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python shared/scripts/generate_peer_review.py <domain> <issue_key>")

    domain = sys.argv[1]
    issue_key = sys.argv[2]
    domain_dir = Path(domain)
    solution_design_path = domain_dir / "docs" / "solution_design.md"
    template_path = Path("shared/templates/peer_review_template.md")
    output_path = domain_dir / "reviews" / f"peer_review_{issue_key.upper()}.md"

    if not solution_design_path.exists():
        raise SystemExit(f"Solution design not found: {solution_design_path}")

    if not template_path.exists():
        raise SystemExit(f"Peer review template not found: {template_path}")

    solution_design = solution_design_path.read_text(encoding="utf-8")
    template = template_path.read_text(encoding="utf-8")
    policies = load_policies()
    findings = build_findings(domain, solution_design, policies)

    review_status = "Pass" if not findings else "Requires Rework"
    overall = build_overall_assessment(findings)

    document = template
    replacements = {
        "{{DOMAIN}}": domain,
        "{{ISSUE_KEY}}": issue_key.upper(),
        "{{REVIEW_STATUS}}": review_status,
        "{{REVIEW_DATE}}": date.today().isoformat(),
        "{{OVERALL_ASSESSMENT}}": overall,
        "{{FINDINGS_TABLE}}": render_findings_table(findings),
        "{{ACTIONS_TABLE}}": render_actions_table(findings),
        "{{REVIEW_DECISION}}": render_review_decision(review_status),
    }

    for placeholder, value in replacements.items():
        document = document.replace(placeholder, value)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding="utf-8")
    print(f"✅ Peer review generated: {output_path}")


def load_policies():
    policy_text = []

    for policy_file in POLICY_FILES:
        path = Path(policy_file)

        if path.exists():
            policy_text.append(path.read_text(encoding="utf-8"))

    return "\n".join(policy_text)


def build_findings(domain, solution_design, policies):
    checks = [
        {
            "id": "ARCH-001",
            "category": "Architecture",
            "severity": "High",
            "location": "Architecture Diagrams",
            "required_terms": ["C1", "C2", "C3", "C4"],
            "comment": "The solution design must reference the complete C1-C4 diagram set.",
            "recommendation": "Ensure C1-C4 sections and diagram references are present and consistent.",
        },
        {
            "id": "SEC-001",
            "category": "Security",
            "severity": "High",
            "location": "Security Design",
            "required_terms": ["authentication", "authorization", "encrypt", "audit", "secrets"],
            "comment": "Security controls need to cover authentication, authorization, encryption, audit logging, and secrets management.",
            "recommendation": "Expand the security design with concrete controls, trust boundaries, and ownership.",
        },
        {
            "id": "DATA-001",
            "category": "Data",
            "severity": "High",
            "location": "Data Design",
            "required_terms": ["data entity", "system of record", "classification", "retention"],
            "comment": "Data ownership, classification, and retention need to be explicit for banking domains.",
            "recommendation": "Classify customer, identity, KYC, and operational data and identify systems of record.",
        },
        {
            "id": "INT-001",
            "category": "Integration",
            "severity": "Medium",
            "location": "Integration Design",
            "required_terms": ["source", "target", "pattern", "protocol"],
            "comment": "Integration patterns and ownership should be clear enough for engineering handover.",
            "recommendation": "Add protocols, sync or async choices, error handling, retry, timeout, and idempotency expectations.",
        },
        {
            "id": "NFR-001",
            "category": "NFR",
            "severity": "Medium",
            "location": "Non-Functional Requirements",
            "required_terms": ["availability", "performance", "scalability", "observability"],
            "comment": "NFRs should be measurable before engineering delivery starts.",
            "recommendation": "Replace placeholders with target availability, latency, throughput, resilience, and observability requirements.",
        },
        {
            "id": "OPS-001",
            "category": "Operations",
            "severity": "Medium",
            "location": "Operational Design",
            "required_terms": ["monitoring", "alerting", "support", "runbook"],
            "comment": "Operational readiness should be visible in the design.",
            "recommendation": "Add monitoring, alerting, ownership, support model, incident response, and runbook references.",
        },
        {
            "id": "REG-001",
            "category": "Regulatory",
            "severity": "Medium",
            "location": "Compliance and Risk",
            "required_terms": ["PCI", "ISO", "regulatory", "audit"],
            "comment": "Bank-relevant regulatory and audit considerations should be clearly linked to controls.",
            "recommendation": "Map relevant banking controls to design mitigations and evidence points.",
        },
    ]

    findings = []
    text = solution_design.lower()

    for check in checks:
        missing_terms = [
            term
            for term in check["required_terms"]
            if term.lower() not in text
        ]

        if missing_terms:
            finding = dict(check)
            finding["missing_terms"] = ", ".join(missing_terms)
            finding["owner"] = "Responsible Architect"
            finding["status"] = "Open"
            findings.append(finding)

    if "tbd" in text or "to be confirmed" in text:
        findings.append(
            {
                "id": "GOV-001",
                "category": "Governance",
                "severity": "Medium",
                "location": "Solution Design",
                "comment": "The design contains placeholders such as TBD or To be confirmed.",
                "recommendation": "Responsible architect should either resolve placeholders or convert them into explicit open actions.",
                "missing_terms": "Resolved design values",
                "owner": "Responsible Architect",
                "status": "Open",
            }
        )

    if policies and "security" not in text:
        findings.append(
            {
                "id": "POL-001",
                "category": "Policy Alignment",
                "severity": "High",
                "location": "Whole Document",
                "comment": "The design does not appear to explicitly align with the shared policy checklist.",
                "recommendation": "Add explicit architecture, security, data, integration, NFR, and regulatory alignment notes.",
                "missing_terms": "Policy alignment narrative",
                "owner": "Responsible Architect",
                "status": "Open",
            }
        )

    return findings


def build_overall_assessment(findings):
    if not findings:
        return "The automated peer review did not identify blocking gaps. Human reviewers should still validate the design before approval."

    high_count = sum(1 for finding in findings if finding["severity"] == "High")
    medium_count = sum(1 for finding in findings if finding["severity"] == "Medium")
    return (
        "The automated peer review identified "
        f"{high_count} high-severity and {medium_count} medium-severity items. "
        "The responsible architect should resolve open findings in the GitHub pull request before the design is approved and published."
    )


def render_findings_table(findings):
    if not findings:
        return "No automated findings were raised."

    rows = [
        "| ID | Category | Severity | Location | Comment | Recommendation | Owner | Status |",
        "|---|---|---|---|---|---|---|---|",
    ]

    for finding in findings:
        rows.append(
            "| {id} | {category} | {severity} | {location} | {comment} | {recommendation} | {owner} | {status} |".format(
                **finding
            )
        )

    return "\n".join(rows)


def render_actions_table(findings):
    if not findings:
        return "No required actions were generated."

    rows = [
        "| ID | Action | Owner | Severity | Status | Resolution |",
        "|---|---|---|---|---|---|",
    ]

    for finding in findings:
        rows.append(
            f"| {finding['id']} | {finding['recommendation']} | {finding['owner']} | {finding['severity']} | Open | Pending responsible architect update |"
        )

    return "\n".join(rows)


def render_review_decision(review_status):
    if review_status == "Pass":
        return "Pass. Human reviewers should still approve the GitHub pull request before publication."

    return (
        "Requires Rework. The responsible architect should update the solution design and diagrams in the pull request, "
        "reply to review comments, and request re-review from the relevant architecture, security, data, and engineering reviewers."
    )


if __name__ == "__main__":
    main()
