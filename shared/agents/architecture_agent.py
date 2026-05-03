import subprocess
import os

def get_base_dir():
    # Goes from shared/agents → project root
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

def run_c1(domain):
    base_dir = get_base_dir()
    script_path = os.path.join(base_dir, "shared", "scripts", "run_c1.sh")

    print(f"Running AI for {domain}...")
    subprocess.run([script_path, domain], check=True)

def get_output_path(domain):
    base_dir = get_base_dir()
    path = os.path.join(base_dir, domain, "diagrams", "C1.svg")
    return os.path.abspath(path)