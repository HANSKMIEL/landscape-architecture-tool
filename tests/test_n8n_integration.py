"""
Tests for N8n integration endpoints and functionality
"""

import json
from unittest.mock import Mock, patch

import pytest
from tests.fixtures.auth_fixtures import authenticated_test_user, setup_test_authentication

from src.main import create_app
from src.models.landscape import db


class TestN8nWebhookEndpoints:
    """Test N8n webhook endpoints that trigger workflows"""

    @pytest.fixture
    def app(self):
        """Create test application with N8n configuration"""
        app = create_app()
        app.config.update(
            {
                "TESTING": True,
                "N8N_BASE_URL": "http://test-n8n:5678",
                "N8N_WEBHOOK_SECRET": "test-secret",
            }
        )

        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()

    @patch("src.routes.webhooks.requests.post")
    def test_project_created_webhook_success(self, mock_post, client):
        """Test successful project created webhook trigger"""
        # Mock successful N8n response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Test data
        data = {
            "project_id": 1,
            "client_id": 1,
            "project_name": "Test Garden Project",
            "created_by": "test_user",
        }

        response = client.post(
            "/webhooks/n8n/project-created",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data["status"] == "workflow_triggered"
        assert response_data["webhook"] == "project-created"

        # Verify the mock was called correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "http://test-n8n:5678/webhook/project-created" in str(call_args)

    @patch("src.routes.webhooks.requests.post")
    def test_project_created_webhook_failure(self, mock_post, client):
        """Test failed project created webhook trigger"""
    # Authentication handled by authenticated_test_user fixture
# Mock failed N8n response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        data = {"project_id": 1, "client_id": 1, "project_name": "Test Garden Project"}

        response = client.post(
            "/webhooks/n8n/project-created",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 500
        response_data = response.get_json()
        assert response_data["status"] == "workflow_failed"

    def test_project_created_webhook_missing_data(self, client, authenticated_test_user):
        """test_project_created_webhook_missing_data"""
        # Authentication handled by authenticated_test_user fixture
        data = {
            "client_id": 1,
            "project_name": "Test Project",
            # Missing project_id
        }

        response = client.post(
            "/webhooks/n8n/project-created",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 400
        response_data = response.get_json()
        assert "project_id is required" in response_data["error"]

    @patch("src.routes.webhooks.requests.post")
    def test_client_updated_webhook(self, mock_post, client):
        """Test client updated webhook trigger"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        data = {
            "client_id": 1,
            "updated_fields": ["email", "phone"],
            "client_data": {"name": "Updated Client", "email": "new@example.com"},
        }

        response = client.post(
            "/webhooks/n8n/client-updated",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data["status"] == "workflow_triggered"
        assert response_data["webhook"] == "client-updated"

    @patch("src.routes.webhooks.requests.post")
    def test_project_milestone_webhook(self, mock_post, client):
        """Test project milestone webhook trigger"""
    # Authentication handled by authenticated_test_user fixture
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        data = {
            "project_id": 1,
            "milestone": "design_completed",
            "status": "completed",
            "completion_percentage": 50,
        }

        response = client.post(
            "/webhooks/n8n/project-milestone",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data["status"] == "workflow_triggered"
        assert response_data["webhook"] == "project-milestone"

    def test_project_milestone_webhook_missing_data(self, client, authenticated_test_user):
        """test_project_milestone_webhook_missing_data"""
        # Authentication handled by authenticated_test_user fixture
        data = {
            "project_id": 1
            # Missing milestone
        }

        response = client.post(
            "/webhooks/n8n/project-milestone",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 400
        response_data = response.get_json()
        assert "project_id and milestone are required" in response_data["error"]

    @patch("src.routes.webhooks.requests.post")
    def test_inventory_alert_webhook(self, mock_post, client):
        """Test inventory alert webhook trigger"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        data = {
            "plant_id": 1,
            "plant_name": "Test Plant",
            "current_stock": 5,
            "minimum_threshold": 10,
            "supplier_id": 1,
        }

        response = client.post(
            "/webhooks/n8n/inventory-alert",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data["status"] == "workflow_triggered"
        assert response_data["webhook"] == "inventory-alert"

    @patch("src.routes.webhooks.requests.post")
    def test_client_onboarding_webhook_success(self, mock_post, client):
        """Test successful client onboarding webhook trigger"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        data = {
            "client_id": 1,
            "client_name": "John Smith",
            "client_email": "john@example.com",
            "contact_person": "John Smith",
            "phone": "+31 20 123 4567",
        }

        response = client.post(
            "/webhooks/n8n/client-onboarding",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data["status"] == "workflow_triggered"
        assert response_data["webhook"] == "client-onboarding"

        # Verify the mock was called correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "http://test-n8n:5678/webhook/client-onboarding" in str(call_args)

    def test_client_onboarding_webhook_missing_data(self, client):
        """Test client onboarding webhook with missing required data"""
        data = {
            "client_name": "John Smith",
            # Missing client_id and client_email
        }

        response = client.post(
            "/webhooks/n8n/client-onboarding",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 400
        response_data = response.get_json()
        assert "client_id and client_email are required" in response_data["error"]


class TestN8nReceiverEndpoints:
    """Test N8n receiver endpoints that handle callbacks"""

    @pytest.fixture
    def app(self):
        """Create test application with N8n configuration"""
        app = create_app()
        app.config.update(
            {
                "TESTING": True,
                "N8N_WEBHOOK_SECRET": None,  # No secret for tests to skip validation
            }
        )

        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()

    def test_email_notification_receiver(self, client):
        """Test receiving email notification from N8n"""
        data = {
            "email_type": "welcome",
            "recipient": "test@example.com",
            "client_id": 1,
            "status": "sent",
            "message_id": "msg123",
        }

        response = client.post(
            "/api/n8n/receive/email-sent",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data["status"] == "received"
        assert "Email notification processed" in response_data["message"]

    def test_task_completion_receiver(self, client):
        """Test receiving task completion from N8n"""
        data = {
            "task_id": "task123",
            "task_type": "document_generation",
            "status": "completed",
            "project_id": 1,
            "result_data": {"file_path": "/path/to/document.pdf"},
        }

        response = client.post(
            "/api/n8n/receive/task-completed",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data["status"] == "received"
        assert "Task completion processed" in response_data["message"]

    def test_task_completion_missing_data(self, client):
        """Test task completion with missing data"""
        data = {
            "task_type": "document_generation",
            "status": "completed",
            # Missing task_id
        }

        response = client.post(
            "/api/n8n/receive/task-completed",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 400
        response_data = response.get_json()
        assert "task_id is required" in response_data["error"]

    def test_external_data_receiver(self, client):
        """Test receiving external data from N8n"""
        data = {
            "source_system": "crm",
            "data_type": "new_lead",
            "payload": {"name": "New Client", "email": "newclient@example.com"},
            "timestamp": "2024-01-01T12:00:00Z",
        }

        response = client.post(
            "/api/n8n/receive/external-data",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data["status"] == "received"
        assert "External data processed" in response_data["message"]

    def test_external_data_missing_source(self, client):
        """Test external data with missing source system"""
        data = {
            "data_type": "new_lead",
            "payload": {"name": "Test"},
            # Missing source_system
        }

        response = client.post(
            "/api/n8n/receive/external-data",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 400
        response_data = response.get_json()
        assert "source_system is required" in response_data["error"]

    @patch("requests.get")
    def test_n8n_status_endpoint_available(self, mock_get, client):
        """Test N8n status when N8n is available"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        response = client.get("/api/n8n/status")

        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data["n8n_integration"] == "enabled"
        assert response_data["n8n_available"] is True
        assert response_data["webhook_secret_configured"] is False  # No secret in test

    @patch("requests.get")
    def test_n8n_status_endpoint_unavailable(self, mock_get, client):
        """Test N8n status when N8n is unavailable"""
        mock_get.side_effect = Exception("Connection failed")

        response = client.get("/api/n8n/status")

        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data["n8n_integration"] == "enabled"
        assert response_data["n8n_available"] is False


class TestN8nSignatureValidation:
    """Test webhook signature validation"""

    @pytest.fixture
    def app(self):
        """Create test application with N8n configuration"""
        app = create_app()
        app.config.update(
            {
                "TESTING": True,
                "N8N_WEBHOOK_SECRET": "test-secret",
            }
        )

        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()

    def test_signature_validation_with_valid_signature(self, client):
        """Test signature validation with valid signature"""
        import hashlib
        import hmac

        data = {"test": "data"}
        json_data = json.dumps(data)

        # Calculate expected signature
        signature = hmac.new(b"test-secret", json_data.encode(), hashlib.sha256).hexdigest()

        response = client.post(
            "/api/n8n/receive/email-sent",
            data=json_data,
            content_type="application/json",
            headers={"X-N8N-Signature": f"sha256={signature}"},
        )

        # Should not return 401 (signature validation passed)
        assert response.status_code != 401

    def test_signature_validation_with_missing_signature(self, client):
        """Test signature validation with missing signature"""
        data = {"test": "data"}

        response = client.post(
            "/api/n8n/receive/email-sent",
            data=json.dumps(data),
            content_type="application/json",
            # No X-N8N-Signature header
        )

        assert response.status_code == 401
        response_data = response.get_json()
        assert "Missing signature" in response_data["error"]

    def test_signature_validation_with_invalid_signature(self, client):
        """Test signature validation with invalid signature"""
        data = {"test": "data"}

        response = client.post(
            "/api/n8n/receive/email-sent",
            data=json.dumps(data),
            content_type="application/json",
            headers={"X-N8N-Signature": "sha256=invalid_signature"},
        )

        assert response.status_code == 401
        response_data = response.get_json()
        assert "Invalid signature" in response_data["error"]

    def test_signature_validation_skipped_when_no_secret(self, client):
        """Test that signature validation is skipped when no secret is configured"""
        # Temporarily remove the secret
        with client.application.app_context():
            client.application.config["N8N_WEBHOOK_SECRET"] = None

            data = {"test": "data"}
            response = client.post(
                "/api/n8n/receive/email-sent",
                data=json.dumps(data),
                content_type="application/json",
                # No signature header, but should still work
            )

            # Should not return 401 (validation skipped)
            assert response.status_code != 401
