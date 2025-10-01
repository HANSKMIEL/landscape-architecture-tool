# DeepSource Integration Setup

This document explains how to configure DeepSource integration for test coverage reporting.

## Overview

DeepSource is a code quality and security analysis platform that has been integrated into the CI/CD pipeline to automatically receive and analyze test coverage reports.

## Configuration Steps

### 1. Get Your DeepSource DSN

1. Visit [DeepSource.io](https://deepsource.io) and sign up or log in
2. Create a new repository or connect your existing GitHub repository
3. Navigate to your repository settings in DeepSource
4. Find the "Data Source Name (DSN)" token - this is a unique identifier for your repository

### 2. Add the DSN to GitHub Secrets

1. Go to your GitHub repository settings
2. Navigate to "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Name: `DEEPSOURCE_DSN`
5. Value: Your DSN token from DeepSource (format: `https://your-dsn-token@deepsource.io/...`)

### 3. Configure DeepSource Repository

Ensure your `.deepsource.toml` file includes the test coverage analyzer:

```toml
[[analyzers]]
name = "test-coverage"

[[analyzers]]
name = "python"

  [analyzers.meta]
  runtime_version = "3.x.x"
```

## How It Works

1. **Test Execution**: The CI/CD pipeline runs tests with coverage reporting enabled
2. **Coverage Generation**: pytest generates `coverage.xml` with detailed coverage data
3. **DeepSource Upload**: If `DEEPSOURCE_DSN` is configured, coverage data is uploaded to DeepSource
4. **Analysis**: DeepSource analyzes the coverage data and provides insights in their dashboard

## Benefits

- **Coverage Tracking**: Monitor test coverage trends over time
- **Pull Request Analysis**: Get coverage reports on pull requests
- **Quality Metrics**: Track code quality improvements alongside coverage
- **Team Insights**: Share coverage reports with the development team

## Troubleshooting

### Pipeline Still Works Without DeepSource

The DeepSource integration is designed to be optional - if the `DEEPSOURCE_DSN` secret is not configured, the pipeline will:
- Still generate coverage reports
- Store coverage as artifacts
- Continue with other pipeline steps
- Not fail due to missing DeepSource configuration

### Common Issues

1. **Invalid DSN**: Ensure the DSN token is copied correctly from DeepSource
2. **Network Issues**: The pipeline handles network connectivity issues gracefully
3. **Repository Not Found**: Ensure the repository is properly configured in DeepSource

## Coverage Artifacts

Even without DeepSource integration, the pipeline stores coverage reports as artifacts:
- `coverage.xml`: Machine-readable coverage data
- `htmlcov/`: Human-readable HTML coverage report

These can be downloaded from the GitHub Actions run page for manual review.

## Verification

Once configured, you should see:
1. Coverage upload messages in the CI/CD logs
2. Coverage data appearing in your DeepSource dashboard
3. Coverage analysis on pull requests (if enabled in DeepSource)

## Support

For issues with:
- **CI/CD Integration**: Check the GitHub Actions logs for error messages
- **DeepSource Configuration**: Refer to [DeepSource Documentation](https://docs.deepsource.io/)
- **Coverage Generation**: Review the pytest and coverage.py configuration