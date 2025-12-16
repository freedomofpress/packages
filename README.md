# FPF Tools RPM packages LFS repo

This repository holds RPM packages served on `packages.freedom.press`.
Currently, this includes [Dangerzone](https://dangerzone.rocks/).

> [!NOTE]
> The code in this repository follows the design choices of
> https://github.com/freedomofpress/securedrop-yum-prod.
>
> As a result, files are kept unmodified as much as possible, to be able to
> apply patches from upstream.

## Prerequisites

- [Podman](http://podman.io/) to run the `tools/publish` script within a container
- [git-lfs](https://git-lfs.github.com/) to store large files
- `rpm-sign`, for signing the packages
- To sign packages, the private key should be in the GPG keyring.

### Git LFS

This repository uses Git LFS to store package files. Git LFS needs to be
enabled and populated before it can work properly:

```bash
# From the branch you want to work with:
git lfs fetch
git lfs install
git lfs checkout
```

## Usage

You can target one of the following branches in this repo, depending on what you
want to do:

- The `main` branch is for packages that will be shipped to end-users.
- The `release` branch is for packages that will be tested by developers.

Starting with freshly built RPM packages, the steps to ship it to the end users
are:

1. Copy package files to each suite in the `dangerzone` folder. If needed,
   prune older versions as new ones are released, to keep the repo manageable
2. Sign packages with `./scripts/sign.py --all`.
3. Prepare the RPM repo and HTML page with `./tools/publish`.
4. Send a pull request that targets the `release` branch.
5. Ensure that the CI completes successfully, meaning that the signatures are
   verified and the repo metadata are in sync.
6. Merge the PR in the `release` branch, which will publish the packages into a
   staging YUM repo. Use this YUM repo for QA purposes.
7. Once QA completes successfully, send a PR to merge `release` into `main`.
8. Ensure that the CI completes successfully, and merge `release` into `main`.

The end users can now upgrade their installation.
