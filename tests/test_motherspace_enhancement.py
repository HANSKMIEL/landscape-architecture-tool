"""
Test for MotherSpace workflow enhancements.
"""

from pathlib import Path

import pytest
import yaml


def test_motherspace_workflow_syntax():
    """Test that the MotherSpace workflow file has valid YAML syntax."""
    workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "motherspace-orchestrator.yml"

    assert workflow_path.exists(), "MotherSpace workflow file should exist"

    with open(workflow_path) as f:
        workflow_content = f.read()

    # Should be valid YAML
    try:
        workflow_data = yaml.safe_load(workflow_content)
        assert workflow_data is not None
    except yaml.YAMLError as e:
        pytest.fail(f"MotherSpace workflow has invalid YAML syntax: {e}")


def test_motherspace_workflow_has_concurrency_and_safety():
    """Test that the MotherSpace workflow includes concurrency control and safety features."""
    workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "motherspace-orchestrator.yml"

    with open(workflow_path) as f:
        workflow_content = f.read()

    workflow_data = yaml.safe_load(workflow_content)

    # Check for concurrency group
    assert "concurrency" in workflow_data, "MotherSpace workflow should include concurrency control"
    
    concurrency = workflow_data["concurrency"]
    assert concurrency.get("group") == "motherspace-orchestrator", "Should have proper concurrency group"
    assert concurrency.get("cancel-in-progress") is False, "Should not cancel in progress runs"

    # Check for actor guard in job condition
    jobs = workflow_data.get("jobs", {})
    orchestrator_job = jobs.get("motherspace_orchestrator", {})
    
    job_if = orchestrator_job.get("if", "")
    assert "github.actor != 'github-actions[bot]'" in job_if, "Should have actor guard to prevent bot loops"
    assert "orchestrate" in job_if, "Should check for 'orchestrate' label"


def test_motherspace_workflow_has_fingerprint_step():
    """Test that the MotherSpace workflow includes fingerprinted issue creation."""
    workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "motherspace-orchestrator.yml"

    with open(workflow_path) as f:
        workflow_content = f.read()

    workflow_data = yaml.safe_load(workflow_content)

    # Check for fingerprint-related step
    jobs = workflow_data.get("jobs", {})
    orchestrator_job = jobs.get("motherspace_orchestrator", {})
    steps = orchestrator_job.get("steps", [])

    step_names = [step.get("name", "") for step in steps]
    
    # Should have create-or-update step
    assert any(
        "Create or Update" in name and "Tracking Issue" in name for name in step_names
    ), "MotherSpace workflow should include create-or-update tracking issue step"

    # Check that fingerprinting logic is present in the workflow
    assert "FINGERPRINT:" in workflow_content, "Workflow should include fingerprinting logic"
    assert "simpleFingerprint" in workflow_content, "Workflow should include fingerprint function"


def test_motherspace_workflow_structure():
    """Test that the MotherSpace workflow maintains proper structure."""
    workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "motherspace-orchestrator.yml"

    with open(workflow_path) as f:
        workflow_content = f.read()

    workflow_data = yaml.safe_load(workflow_content)

    # Check basic workflow structure
    assert "name" in workflow_data
    assert "on" in workflow_data or True in workflow_data  # YAML may parse 'on:' as boolean True
    assert "jobs" in workflow_data

    # Check job structure
    jobs = workflow_data["jobs"]
    assert "motherspace_orchestrator" in jobs

    orchestrator_job = jobs["motherspace_orchestrator"]
    assert "runs-on" in orchestrator_job
    assert "steps" in orchestrator_job

    # Verify environment variables
    env = orchestrator_job.get("env", {})
    assert "MOTHERSPACE_VERSION" in env
    assert "HARMONY_THRESHOLD" in env
    assert "SECURITY_LEVEL" in env


def test_issue_management_keywords_present():
    """Test that issue management keywords are present in the workflow."""
    workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "motherspace-orchestrator.yml"

    with open(workflow_path) as f:
        workflow_content = f.read()

    # Check for key functionality keywords
    required_keywords = [
        "automated issues",
        "deduplication",
        "calculateIssueSimilarity",
        "pr_safe_operations",
        "routine_tasks",
        "copilot delegation",
        "willInterfereWithPRs",
    ]

    for keyword in required_keywords:
        assert keyword in workflow_content, f"MotherSpace workflow should contain '{keyword}' functionality"


def test_motherspace_version_updated():
    """Test that MotherSpace version reflects the enhancement."""
    workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "motherspace-orchestrator.yml"

    with open(workflow_path) as f:
        workflow_content = f.read()

    workflow_data = yaml.safe_load(workflow_content)

    # Check version
    env = workflow_data["jobs"]["motherspace_orchestrator"]["env"]
    version = env.get("MOTHERSPACE_VERSION", "")

    # Version should be 1.1.0 or higher (indicates enhancement)
    assert version, "MotherSpace version should be defined"

    # Parse version for comparison
    version_parts = version.split(".")
    major, minor = int(version_parts[0]), int(version_parts[1])

    assert major >= 1, f"MotherSpace major version should be 1 or higher, got {version}"
    assert (
        minor >= 1
    ), f"MotherSpace minor version should be 1 or higher to include issue management enhancement, got {version}"
