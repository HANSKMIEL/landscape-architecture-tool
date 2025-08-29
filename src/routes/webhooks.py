"""
Webhook routes for N8n integration.
These endpoints allow the Landscape Tool to trigger N8n workflows.
"""

import logging
from datetime import datetime, timezone

import requests
from flask import Blueprint, current_app, jsonify, request

from src.models.landscape import db  # noqa: F401,E501 - Future webhook persistence
from src.utils.error_handlers import handle_errors

logger = logging.getLogger(__name__)
bp = Blueprint("webhooks", __name__, url_prefix="/webhooks")


def trigger_n8n_workflow(webhook_url, data):
    """
    Helper function to trigger N8n workflows via webhook
    """
    try:
        n8n_base_url = current_app.config.get(
            "N8N_BASE_URL", "http://localhost:5678"
        )  # noqa: E501
        full_url = f"{n8n_base_url}/webhook/{webhook_url}"

        response = requests.post(
            full_url,
            json=data,
            timeout=30,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            logger.info(f"Successfully triggered N8n workflow: {webhook_url}")
            return True
        else:
            logger.error(
                f"Failed to trigger N8n workflow: {webhook_url}, "
                f"Status: {response.status_code}"
            )
            return False

    except requests.RequestException as e:
        logger.error(f"Error triggering N8n workflow {webhook_url}: {str(e)}")
        return False


@bp.route("/n8n/project-created", methods=["POST"])
@handle_errors
def trigger_project_created():
    """
    Trigger N8n workflow when a new project is created
    Expected payload: {
        'project_id': int, 'client_id': int, 'project_name': str
    }
    """
    data = request.get_json()

    if not data or "project_id" not in data:
        return jsonify({"error": "project_id is required"}), 400

    # Prepare data for N8n workflow
    workflow_data = {
        "event": "project_created",
        "project_id": data["project_id"],
        "client_id": data.get("client_id"),
        "project_name": data.get("project_name"),
        "timestamp": data.get(
            "timestamp", datetime.now(timezone.utc).isoformat()
        ),  # noqa: E501
        "created_by": data.get("created_by"),
    }

    success = trigger_n8n_workflow("project-created", workflow_data)

    if success:
        return (
            jsonify(
                {"status": "workflow_triggered", "webhook": "project-created"}
            ),  # noqa: E501
            200,
        )
    else:
        return (
            jsonify({"status": "workflow_failed", "webhook": "project-created"}),  # noqa: E501
            500,
        )  # noqa: E501


@bp.route("/n8n/client-updated", methods=["POST"])
@handle_errors
def trigger_client_updated():
    """
    Trigger N8n workflow when client information is updated  # noqa: E501
    Expected payload: {'client_id': int, 'updated_fields': list, 'client_data': dict}  # noqa: E501
    """
    data = request.get_json()

    if not data or "client_id" not in data:
        return jsonify({"error": "client_id is required"}), 400

    workflow_data = {
        "event": "client_updated",
        "client_id": data["client_id"],
        "updated_fields": data.get("updated_fields", []),
        "client_data": data.get("client_data", {}),
        "timestamp": data.get(
            "timestamp", datetime.now(timezone.utc).isoformat()
        ),  # noqa: E501
    }

    success = trigger_n8n_workflow("client-updated", workflow_data)

    if success:
        return (
            jsonify(
                {"status": "workflow_triggered", "webhook": "client-updated"}
            ),  # noqa: E501
            200,
        )
    else:
        return (
            jsonify({"status": "workflow_failed", "webhook": "client-updated"}),  # noqa: E501
            500,
        )  # noqa: E501


@bp.route("/n8n/project-milestone", methods=["POST"])
@handle_errors
def trigger_project_milestone():
    """
    Trigger N8n workflow when a project reaches a milestone  # noqa: E501
    Expected payload: {'project_id': int, 'milestone': str, 'status': str}
    """
    data = request.get_json()

    if not data or "project_id" not in data or "milestone" not in data:
        return jsonify({"error": "project_id and milestone are required"}), 400

    workflow_data = {
        "event": "project_milestone",
        "project_id": data["project_id"],
        "milestone": data["milestone"],
        "status": data.get("status"),
        "completion_percentage": data.get("completion_percentage"),
        "timestamp": data.get(
            "timestamp", datetime.now(timezone.utc).isoformat()
        ),  # noqa: E501
    }

    success = trigger_n8n_workflow("project-milestone", workflow_data)

    if success:
        return (
            jsonify(
                {"status": "workflow_triggered", "webhook": "project-milestone"}  # noqa: E501
            ),  # noqa: E501
            200,
        )
    else:
        return (
            jsonify(
                {"status": "workflow_failed", "webhook": "project-milestone"}
            ),  # noqa: E501
            500,
        )


@bp.route("/n8n/inventory-alert", methods=["POST"])
@handle_errors
def trigger_inventory_alert():
    """
    Trigger N8n workflow for low inventory alerts  # noqa: E501
    Expected payload: {'plant_id': int, 'current_stock': int, 'minimum_threshold': int}  # noqa: E501
    """
    data = request.get_json()

    if not data or "plant_id" not in data:
        return jsonify({"error": "plant_id is required"}), 400

    workflow_data = {
        "event": "inventory_alert",
        "plant_id": data["plant_id"],
        "plant_name": data.get("plant_name"),
        "current_stock": data.get("current_stock", 0),
        "minimum_threshold": data.get("minimum_threshold", 0),
        "supplier_id": data.get("supplier_id"),
        "timestamp": data.get(
            "timestamp", datetime.now(timezone.utc).isoformat()
        ),  # noqa: E501
    }

    success = trigger_n8n_workflow("inventory-alert", workflow_data)

    if success:
        return (
            jsonify(
                {"status": "workflow_triggered", "webhook": "inventory-alert"}
            ),  # noqa: E501
            200,
        )
    else:
        return (
            jsonify({"status": "workflow_failed", "webhook": "inventory-alert"}),  # noqa: E501
            500,
        )  # noqa: E501
