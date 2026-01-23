# Packages for FPF tools

This repository holds DEB and RPM packages served on `packages.freedom.press`.
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
- `rpm-sign`, for signing the RPM packages
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

## Workflow

You can target one of the following branches in this repo, depending on what you
want to do:

- The `main` branch is for packages that will be shipped to end-users
  (https://packages.freedom.press)
- The `release` branch is for packages that will be tested by developers
  (https://packages-qa.freedom.press)

### Sign RPM packages (`yum-tools-prod`)

Starting with freshly built RPM packages, the first step is to place them in the
proper directory and sign them.

1. Change directory to `yum-tools-prod/`
2. Copy package files to each suite in the `dangerzone` folder. If needed,
   prune older versions as new ones are released, to keep the repo manageable
3. Sign packages with `./scripts/sign.py --all`.

### Sign DEB packages (`apt-tools-prod/`)

Same applies to new DEB packages.

1. Change directory to `apt-tools-prod/`
2. Add new package files to each suite in `dangerzone`. You may want to
   prune older versions as new ones are released, to keep the repo
   manageable. You can use the scripts located in `./tools` for this:

   * `./tools/remove-version X.Y.Z` will remove all Dangerzone packages from the
     repository that match a specific version.
   * `./tools/add-version` will get the debian file from the main dangerzone
     repository, put it in the proper folder and create symlinks.
   * `./tools/reset-repo` will reset the repository, it can be useful before
     publishing it.

3. Run `./tools/sign` to sign the release files. This part must run
   on an environment that has access to the private PGP key.

> [!NOTE]
>
> You need to do the following when adding and/or removing a distribution:
>
> - Update the `dangerzone/*` folders accordingly. They are named after the distribution version
> - Update the `repo/conf/distributions` file and add/remove your distribution version.
> - Update the `.github/workflows/ci.yaml` file, with the updated distribution list.

### Publish the repo to package-qa.freedom.press (for testing)

1. Change directory to the root of this repo.
2. Generate the HTML pages for the APT and YUM repos using `./tools/publish`.
3. Send a pull request that targets the `release` branch.
4. Ensure that the CI completes successfully, meaning that the signatures are
   verified and the repo metadata are in sync.
5. Merge the PR in the `release` branch, which will publish the packages to
   https://packages-qa.freedom.press for QA purposes:
   * To test the APT repo, change https://packages.freedom.press to
     https://packages-qa.freedom.press in the installation instructions.
   * To test the YUM repo, use this command:

     ```
     sudo dnf config-manager addrepo --from-repofile=https://packages-qa.freedom.press/yum-tools-prod/dangerzone/dangerzone-qa.repo
     ```

### Publish the repo to packages.freedom.press (final)

1. Once QA completes successfully, send a PR to merge `release` into `main`.
2. Ensure that the CI completes successfully, and merge `release` into `main`.

The end users can now upgrade their installation.
