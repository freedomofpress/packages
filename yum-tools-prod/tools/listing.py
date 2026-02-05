#!/usr/bin/env python3

from collections import defaultdict
from pathlib import Path
import rpm
import os
import shutil

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


def parse_rpm_repo(repo_path):
    """Parse RPM repository structure and extract package information"""
    result = {}

    # RPM repositories are often organized by release/version
    # Let's check for common directory structures
    release_dirs = {rpm.parent for rpm in repo_path.glob("**/*.rpm")}
    release_dirs = [(dir.name, dir) for dir in sorted(release_dirs)]

    # Process each release directory
    for release_name, release_path in release_dirs:
        result[release_name] = {"components": {}}

        result[release_name]["components"] = defaultdict(list)

        for rpm_file in sorted(release_path.glob("*.rpm")):
            # Use rpm module to extract package information
            ts = rpm.TransactionSet()
            ts.setVSFlags(rpm._RPMVSF_NOSIGNATURES)

            with open(rpm_file, "rb") as f:
                hdr = ts.hdrFromFdno(f.fileno())

                # Calculate relative path for download link
                rel_path = rpm_file.relative_to(repo_path)
                download_link = f"/yum-tools-prod/{rel_path}"

                package_info = {
                    "name": hdr[rpm.RPMTAG_NAME],
                    "version": f"{hdr[rpm.RPMTAG_VERSION]}-{hdr[rpm.RPMTAG_RELEASE]}",
                    "size": format_size(os.path.getsize(rpm_file)),
                    "description": hdr[rpm.RPMTAG_SUMMARY],
                    "architecture": hdr[rpm.RPMTAG_ARCH],
                    "download_link": download_link,
                    "filename": rpm_file.name,
                }

                result[release_name]["components"][hdr[rpm.RPMTAG_ARCH]].append(
                    package_info
                )

    if not any(
        comps for rel in result.values() for comps in rel["components"].values()
    ):
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
    return template.render(repo_data=repo_data, title="FPF Tools Yum Repository")


def main():
    repo_path = Path(__file__).parents[2] / "public" / "yum-tools-prod"
    repo_data = parse_rpm_repo(repo_path)
    html_output = generate_html(repo_data)
    index_html = repo_path / "index.html"
    index_html.write_text(html_output)
    shutil.copyfile(
        Path(__file__).parents[2] / "templates" / "listing" / "styles.css",
        repo_path / "styles.css",
    )

    # The location of the GPG key is very sensitive, because it seems that some
    # Fedora-based distros fetch it every time they need to update their
    # packages. We have already changed its location once, and this broke
    # updates for existing users: https://github.com/freedomofpress/packages/issues/54
    #
    # Here, we add a copy to the original location, to make updates work again.
    shutil.copyfile(
        Path(__file__).parents[1] / "dangerzone" / "fpf-yum-tools-archive-keyring.gpg",
        repo_path / "fpf-yum-tools-archive-keyring.gpg",
    )

    print(f"Updated {index_html}")


if __name__ == "__main__":
    main()
