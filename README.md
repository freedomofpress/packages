# FPF Tools RPM packages LFS repo

This repository holds RPM packages served on `packages.freedom.press`.
Currently, this includes [Dangerzone](https://dangerzone.rocks/).

> [!NOTE]
> The code in this repository is mainly a reproduction of how the SecureDrop
> team is handling their packages.
>
> As a result, files are kept unmodified as much as possible, to be able to
> apply patches from upstream.

## Prerequisites

- [Podman](http://podman.io/) to run the `publish` script within a container ;
- [git-lfs](https://git-lfs.github.com/) to store large files ;
- `rpm-sign`, for signing the packages ;
- To sign packages, the private key should be in the GPG keyring.

### Git LFS

This repository uses Git LFS to store package files. Git LFS needs to be
enabled and populated before it can work properly:

```bash
# From the branch you want to work with:
git lfs fetch
git lfs install
git lfs checkout
```

## Usage

It is possible to publish to the following branches, depending the intention:

- The `main` branch is for user-facing packages
- The `release` branch is targetted at developers.

The usual workflow is to first publish to the `release` branch, and when the QA
passes, merge it onto `main`.

To publish a new package, from the release machine, the workflow is as follows:

1. Copy package files to each suite in the `dangerzone` folder. If needed,
   prune older versions as new ones are released, to keep the repo manageable ;
2. Sign packages with `./scripts/sign.py --all` ;
3. Prepare the RPM repo and HTML page with `./tools/publish`
4. Create a pull request on a specific branch that targets `main` or `release`
5. The CI will run, and signatures will be checked against the known public ;
6. After a merge, resulting files will be available to either A or B links as a
   result.


