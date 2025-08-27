# FPF Tools RPM packages LFS repo

This repository holds RPM packages served on `packages.freedom.press`.
Currently, this includes [Dangerzone](https://dangerzone.rocks/).

## Prerequisites

- A Fedora machine, since we will use the RPM toolchain.
- [git-lfs](https://git-lfs.github.com/) to store large files.
- `rpm-sign`, for signing the packages.

## Usage

- Set up a machine with the GPG key used for signing/verifying RPMs.

- Copy package files to each suite in `dangerzone`. You may want to
  prune older versions as new ones are released, to keep the repo
  manageable.

- Sign packages with `./scripts/sign.py --all`. You need the private key
  in the GPG keyring for this action.

- Verify package signatures with `./scripts/check.py --all`.
