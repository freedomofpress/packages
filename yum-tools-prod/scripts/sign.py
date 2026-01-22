#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from pathlib import Path


def iter_all_rpms():
    root = Path(__file__).parent.parent
    yield from root.glob("**/*.rpm")


def sign_rpm(path, key_id):
    # NOTE: Taken from
    # https://hussainaliakbar.github.io/signing-and-verifying-rpm-packages/
    print(f">> Signing {path}")
    try:
        subprocess.check_call(
            [
                "rpm",
                "--define",
                f"_gpg_name {key_id}",
                "--addsign",
                path,
            ]
        )
    except subprocess.CalledProcessError as e:
        fail(f"Error signing package {path}: {e}")


def sign_all_rpms(key_id):
    for rpm in iter_all_rpms():
        if not str(rpm).startswith("public/"):
            sign_rpm(rpm, key_id)


def fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", default=False)
    parser.add_argument(
        "--key-id",
        type=str,
        help="The key ID that will be used",
        default="Dangerzone Release Key <dangerzone-release-key@freedom.press>",
    )
    parser.add_argument("packages", type=str, nargs="*", help="Files to sign/verify")
    args = parser.parse_args()

    # Fail if no package is specified or not using '--all'
    if not args.all and not args.packages:
        fail("Please specify an rpm package or --all")

    if args.all:
        sign_all_rpms(args.key_id)
    else:
        for package in args.packages:
            assert os.path.exists(package)
            sign_rpm(package, args.key_id)


if __name__ == "__main__":
    main()
