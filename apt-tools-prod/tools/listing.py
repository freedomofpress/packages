#!/usr/bin/env python3

import shutil
import subprocess
from datetime import datetime, UTC
from pathlib import Path

from debian import deb822
from jinja2 import Environment, FileSystemLoader, select_autoescape


def format_size(size_bytes):
    """Convert size in bytes to human-readable format"""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f}MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f}GB"


def commit_info(repo_path: Path, codename: str, component: str, pkginfo) -> (str, str):
    deb_path = Path(pkginfo["Filename"]).name
    object_id = subprocess.check_output(
        [
            "git",
            "hash-object",
            repo_path / Path(pkginfo["Filename"]),
        ],
        text=True,
    ).strip()
    if not object_id:
        raise RuntimeError(f"Error: No Git object ID found for {deb_path}")

    # Find the commit in which the file was added
    output = subprocess.check_output(
        [
            "git",
            "log",
            "--format=%H|%ai",
            "--find-object",
            object_id,
        ],
        text=True,
    ).strip()
    if not output:
        raise RuntimeError(f"Error: No commit found for {deb_path}")

    commit, date = output.split("\n")[-1].split("|")
    date = str(datetime.fromisoformat(date).astimezone(UTC)).split("+")[0]
    return commit, date


def parse_apt_repo(apt_root: Path, repo_base_path: Path):
    """Parse APT repository structure and extract package information"""
    result = {}

    # Find all dists directories
    dists_path = repo_base_path / "dists"
    if not dists_path.exists():
        raise RuntimeError(f"Error: {dists_path} does not exist")

    # Iterate through each codename (e.g., bullseye, bookworm)
    for codename_dir in sorted(dists_path.iterdir()):
        if not codename_dir.is_dir():
            continue

        # Parse Release file to get distribution information
        release_file = codename_dir / "Release"
        if not release_file.exists():
            raise RuntimeError(f"Error: No Release file found for {codename_dir.name}")

        result[codename_dir.name] = {"components": {}}

        # Find all components (e.g., main, contrib, non-free)
        for component_dir in sorted(codename_dir.iterdir()):
            if not component_dir.is_dir():
                continue

            result[codename_dir.name]["components"][component_dir.name] = []

            # Find all binary package indexes
            for packages_path in sorted(component_dir.glob("binary-*/Packages")):
                with packages_path.open("rb") as f:
                    for pkg in deb822.Packages.iter_paragraphs(f):
                        commit, date = commit_info(
                            repo_base_path, codename_dir.name, component_dir.name, pkg
                        )
                        # Extract filename for download link
                        filename = pkg["Filename"]
                        # Construct the download link relative to the repo base
                        download_link = str(Path("/") / filename)

                        package_info = {
                            "name": pkg["Package"],
                            "version": pkg["Version"],
                            "size": format_size(int(pkg["Size"])),
                            "description": pkg["Description"].split("\n")[0],
                            "architecture": pkg["Architecture"],
                            "download_link": download_link,
                            "filename": Path(filename).name,
                            "commit": commit,
                            "date": date,
                        }
                        result[codename_dir.name]["components"][
                            component_dir.name
                        ].append(package_info)

    if not result:
        raise RuntimeError("Error: No packages found in the repository")
    return result


def generate_html(repo_data):
    """Generate HTML output using Jinja2 templating with autoescaping enabled"""

    # Create template with autoescaping enabled
    env = Environment(
        loader=FileSystemLoader(Path(__file__).parents[2] / "templates" / "listing"),
        autoescape=select_autoescape(["html", "xml"]),
    )

    # Load the template from file
    template = env.get_template("index.html.j2")
    return template.render(
        repo_data=repo_data,
        title="FPF tools APT Repository",
        repo_name="freedomofpress/apt-tools-prod",
    )


def main():
    git_root = Path(__file__).parents[2]
    apt_root = git_root / "apt-tools-prod"
    repo_path = git_root / "public" / "apt-tools-prod"
    repo_data = parse_apt_repo(apt_root, repo_path)
    html_output = generate_html(repo_data)
    (repo_path / "index.html").write_text(html_output)
    shutil.copyfile(
        Path(__file__).parents[2] / "templates" / "listing" / "styles.css",
        repo_path / "styles.css",
    )


if __name__ == "__main__":
    main()
