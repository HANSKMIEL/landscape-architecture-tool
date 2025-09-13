# Branch Protection Rules

To ensure the stability and quality of the `main` branch, the following branch protection rules should be implemented in the repository settings:

## Rule: `main` branch

- **Require a pull request before merging**: This ensures that all changes to the `main` branch are reviewed and approved before being merged.
- **Require status checks to pass before merging**: This ensures that all automated tests and quality checks pass before a pull request can be merged.
- **Require conversation resolution before merging**: This ensures that all comments and discussions on a pull request are resolved before it can be merged.
- **Require signed commits**: This ensures that all commits to the `main` branch are signed and verified.
- **Restrict who can push to this branch**: This prevents direct pushes to the `main` branch and ensures that all changes go through the pull request process.
- **Allow force pushes**: This should be disabled to prevent the rewriting of the `main` branch history.
- **Allow deletions**: This should be disabled to prevent the accidental deletion of the `main` branch.
