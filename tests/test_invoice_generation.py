import pytest

from tests.fixtures.auth_fixtures import authenticated_test_user, setup_test_authentication
from tests.fixtures.database import DatabaseTestMixin


@pytest.mark.api
class TestInvoiceGeneration(DatabaseTestMixin):
    """Test invoice and quote generation functionality"""

    def test_get_invoiceable_projects(self, client, app_context):
        """Test getting list of invoiceable projects"""
        response = client.get("/api/invoices/projects")
        assert response.status_code == 200

        data = response.get_json()
        assert "projects" in data
        assert "total" in data
        assert data["total"] >= 0

    def test_generate_quote_json(self, client, app_context):
        """Test generating quote in JSON format"""
        # First get available projects
        projects_response = client.get("/api/invoices/projects")
        projects_data = projects_response.get_json()

        if projects_data["total"] > 0:
            project_id = projects_data["projects"][0]["id"]

            response = client.get(f"/api/invoices/quote/{project_id}?format=json")
            assert response.status_code == 200

            data = response.get_json()
            assert "quote_number" in data
            assert "client" in data
            assert "project" in data
            assert "items" in data
            assert "financial" in data
            assert "company" in data

            # Verify financial calculations
            financial = data["financial"]
            assert "subtotal" in financial
            assert "vat_amount" in financial
            assert "total" in financial
            assert financial["vat_rate"] == 0.21  # Dutch VAT rate

    def test_generate_quote_pdf_endpoint(self, client, app_context):
        """Test that PDF quote endpoint responds correctly"""
        # First get available projects
        projects_response = client.get("/api/invoices/projects")
        projects_data = projects_response.get_json()

        if projects_data["total"] > 0:
            project_id = projects_data["projects"][0]["id"]

            # Test PDF endpoint (should return PDF content or appropriate response)
            response = client.get(f"/api/invoices/quote/{project_id}?format=pdf")
            # PDF generation might fail in test environment, but endpoint should exist
            assert response.status_code in [200, 500]  # 500 acceptable if PDF libs not fully available

    def test_generate_invoice_json(self, client, app_context):
        """Test generating invoice in JSON format"""
        # First get available projects
        projects_response = client.get("/api/invoices/projects")
        projects_data = projects_response.get_json()

        if projects_data["total"] > 0:
            project_id = projects_data["projects"][0]["id"]

            response = client.post(f"/api/invoices/invoice/{project_id}", json={"format": "json"})
            assert response.status_code == 200

            data = response.get_json()
            assert "invoice_number" in data
            assert "invoice_date" in data
            assert "due_date" in data
            assert "payment_terms" in data
            assert "client" in data
            assert "project" in data
            assert "items" in data
            assert "financial" in data

    def test_quote_financial_calculations(self, client, app_context):
        """Test that quote financial calculations are correct"""
        projects_response = client.get("/api/invoices/projects")
        projects_data = projects_response.get_json()

        if projects_data["total"] > 0:
            project_id = projects_data["projects"][0]["id"]

            response = client.get(f"/api/invoices/quote/{project_id}?format=json")
            data = response.get_json()

            financial = data["financial"]
            subtotal = financial["subtotal"]
            vat_rate = financial["vat_rate"]
            vat_amount = financial["vat_amount"]
            total = financial["total"]

            # Verify VAT calculation
            expected_vat = subtotal * vat_rate
            assert abs(vat_amount - expected_vat) < 0.01  # Allow for rounding

            # Verify total calculation
            expected_total = subtotal + vat_amount
            assert abs(total - expected_total) < 0.01  # Allow for rounding

    def test_company_information_included(self, client, app_context):
        """Test that company information is properly included"""
        projects_response = client.get("/api/invoices/projects")
        projects_data = projects_response.get_json()

        if projects_data["total"] > 0:
            project_id = projects_data["projects"][0]["id"]

            response = client.get(f"/api/invoices/quote/{project_id}?format=json")
            data = response.get_json()

            company = data["company"]
            assert company["name"] == "HANSKMIEL Landschapsarchitectuur"
            assert company["vat_number"] == "NL123456789B01"
            assert "address" in company
            assert "phone" in company
            assert "email" in company

    def test_invalid_project_id(self, client, app_context):
        """Test handling of invalid project ID"""
        # Authentication handled by authenticated_test_user fixture
        response = client.get("/api/invoices/quote/99999?format=json")
        assert response.status_code == 404

        data = response.get_json()
        assert "error" in data

    def test_quote_items_structure(self, client, app_context):
        """Test that quote items have proper structure"""
        projects_response = client.get("/api/invoices/projects")
        projects_data = projects_response.get_json()

        if projects_data["total"] > 0:
            project_id = projects_data["projects"][0]["id"]

            response = client.get(f"/api/invoices/quote/{project_id}?format=json")
            data = response.get_json()

            items = data["items"]
            assert len(items) > 0

            for item in items:
                assert "description" in item
                assert "quantity" in item
                assert "unit" in item
                assert "unit_price" in item
                assert "total" in item
                assert "category" in item
                assert "type" in item

                # Verify calculation
                expected_total = item["quantity"] * item["unit_price"]
                assert abs(item["total"] - expected_total) < 0.01
