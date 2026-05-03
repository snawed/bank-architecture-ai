import os
import subprocess


def get_base_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))


def generate_peer_review(domain, issue_key):
    base_dir = get_base_dir()
    python_bin = os.path.join(base_dir, ".venv", "bin", "python")

    if not os.path.exists(python_bin):
        python_bin = "python3"

    subprocess.run(
        [
            python_bin,
            "-m",
            "shared.scripts.generate_peer_review",
            domain,
            issue_key,
        ],
        cwd=base_dir,
        check=True,
    )


def get_peer_review_path(domain, issue_key):
    base_dir = get_base_dir()
    path = os.path.join(base_dir, domain, "reviews", f"peer_review_{issue_key.upper()}.md")
    return os.path.abspath(path)
