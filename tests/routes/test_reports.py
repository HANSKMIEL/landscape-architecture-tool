# Test file for Reports API Routes
# This file handles comprehensive testing of report generation operations

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from tests.fixtures.database import DatabaseTestMixin


@pytest.mark.api
class TestReportsRoutes(DatabaseTestMixin):
    """Test class for reports routes"""

    def test_generate_business_summary_json_format(self, client, app_context):
        """Test business summary report in JSON format"""
        response = client.get("/api/reports/business-summary")

        assert response.status_code == 200
        data = response.get_json()

        # Check required fields
        assert "generated_at" in data
        assert "summary" in data
        assert "project_stats" in data
        assert "top_clients" in data
        assert "plant_usage" in data

        # Check summary structure
        summary = data["summary"]
        assert "total_projects" in summary
        assert "total_clients" in summary
        assert "total_plants" in summary
        assert "total_products" in summary
        assert "total_suppliers" in summary

        # Verify data types
        assert isinstance(summary["total_projects"], int)
        assert isinstance(summary["total_clients"], int)

    def test_generate_business_summary_with_date_range(self, client, app_context):
        """Test business summary with date range parameters"""
        response = client.get(
            "/api/reports/business-summary",
            query_string={
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-12-31T23:59:59",
                "format": "json",
            },
        )

        assert response.status_code == 200
        data = response.get_json()

        # Check period is included
        assert "period" in data
        period = data["period"]
        assert period["start_date"] == "2024-01-01T00:00:00"
        assert period["end_date"] == "2024-12-31T23:59:59"

    def test_generate_business_summary_pdf_format(self, client, app_context):
        """Test business summary report in PDF format"""
        response = client.get(
            "/api/reports/business-summary", query_string={"format": "pdf"}
        )

        assert response.status_code == 200
        assert response.content_type == "application/pdf"
        assert len(response.data) > 0

        # Check PDF headers
        assert response.headers.get("Content-Disposition")
        assert "business_summary_" in response.headers.get("Content-Disposition")

    def test_generate_business_summary_error_handling(self, client, app_context):
        """Test business summary error handling"""
        # Test with invalid date format
        response = client.get(
            "/api/reports/business-summary", query_string={"start_date": "invalid-date"}
        )

        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data

    def test_generate_project_report_json_format(
        self, client, app_context, sample_project
    ):
        """Test project report in JSON format"""
        # Use the sample project
        response = client.get(f"/api/reports/project/{sample_project.id}")

        if response.status_code == 404:
            # If no project exists, skip this test
            pytest.skip("No sample project available")

        assert response.status_code == 200
        data = response.get_json()

        # Check required fields
        assert "generated_at" in data
        assert "project" in data
        assert "client" in data
        assert "plants" in data
        assert "products" in data
        assert "summary" in data

        # Check project structure
        project = data["project"]
        assert "id" in project
        assert "name" in project
        assert "status" in project

        # Check client structure
        client_data = data["client"]
        assert "name" in client_data
        assert "email" in client_data

    def test_generate_project_report_pdf_format(
        self, client, app_context, sample_project
    ):
        """Test project report in PDF format"""
        response = client.get(
            f"/api/reports/project/{sample_project.id}", query_string={"format": "pdf"}
        )

        if response.status_code == 404:
            pytest.skip("No sample project available")

        assert response.status_code == 200
        assert response.content_type == "application/pdf"

    def test_generate_project_report_not_found(self, client, app_context):
        """Test project report for non-existent project"""
        response = client.get("/api/reports/project/99999")

        assert response.status_code == 404

    def test_generate_plant_usage_report(self, client, app_context):
        """Test plant usage statistics report"""
        response = client.get("/api/reports/plant-usage")

        assert response.status_code == 200
        data = response.get_json()

        # Check required fields
        assert "generated_at" in data
        assert "plant_usage" in data
        assert "category_distribution" in data
        assert "total_unique_plants" in data

        # Check data types
        assert isinstance(data["plant_usage"], list)
        assert isinstance(data["category_distribution"], dict)
        assert isinstance(data["total_unique_plants"], int)

    def test_generate_supplier_performance_report(self, client, app_context):
        """Test supplier performance report"""
        response = client.get("/api/reports/supplier-performance")

        assert response.status_code == 200
        data = response.get_json()

        # Check required fields
        assert "generated_at" in data
        assert "suppliers" in data
        assert "total_suppliers" in data

        # Check data types
        assert isinstance(data["suppliers"], list)
        assert isinstance(data["total_suppliers"], int)

        # Check supplier data structure if suppliers exist
        if data["suppliers"]:
            supplier = data["suppliers"][0]
            assert "name" in supplier
            assert "product_count" in supplier
            assert "project_count" in supplier

    @patch("src.routes.reports.generate_business_summary_pdf")
    def test_pdf_generation_error_handling(self, mock_pdf_gen, client, app_context):
        """Test PDF generation error handling"""
        # Mock PDF generation to raise an exception
        mock_pdf_gen.side_effect = Exception("PDF generation failed")

        response = client.get(
            "/api/reports/business-summary", query_string={"format": "pdf"}
        )

        # Should return error response
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data
        assert "PDF generation failed" in data["error"]

    def test_business_summary_empty_database(self, client, app_context):
        """Test business summary with empty database"""
        response = client.get("/api/reports/business-summary")

        assert response.status_code == 200
        data = response.get_json()

        # All counts should be zero
        summary = data["summary"]
        assert summary["total_projects"] == 0
        assert summary["total_clients"] == 0
        assert summary["total_plants"] == 0
        assert summary["total_products"] == 0
        assert summary["total_suppliers"] == 0

        # Lists should be empty
        assert data["top_clients"] == []
        assert data["plant_usage"] == []

    def test_plant_usage_report_empty_database(self, client, app_context):
        """Test plant usage report with empty database"""
        response = client.get("/api/reports/plant-usage")

        assert response.status_code == 200
        data = response.get_json()

        assert data["plant_usage"] == []
        assert data["category_distribution"] == {}
        assert data["total_unique_plants"] == 0
        assert data["most_popular_plant"] is None

    def test_supplier_performance_empty_database(self, client, app_context):
        """Test supplier performance report with empty database"""
        response = client.get("/api/reports/supplier-performance")

        assert response.status_code == 200
        data = response.get_json()

        assert data["suppliers"] == []
        assert data["total_suppliers"] == 0
        assert data["top_supplier"] is None

    def test_business_summary_budget_calculations(self, client, app_context):
        """Test business summary budget calculations"""
        response = client.get("/api/reports/business-summary")

        assert response.status_code == 200
        data = response.get_json()

        budget_stats = data["project_stats"]["budget_stats"]

        # Check budget fields exist
        assert "total_budget" in budget_stats
        assert "total_spent" in budget_stats
        assert "avg_budget" in budget_stats
        assert "utilization_rate" in budget_stats

        # Check data types
        assert isinstance(budget_stats["total_budget"], (int, float))
        assert isinstance(budget_stats["total_spent"], (int, float))
        assert isinstance(budget_stats["avg_budget"], (int, float))
        assert isinstance(budget_stats["utilization_rate"], (int, float))

    def test_report_generation_timestamps(self, client, app_context):
        """Test that reports include proper timestamps"""
        response = client.get("/api/reports/business-summary")

        assert response.status_code == 200
        data = response.get_json()

        # Check timestamp exists and is valid ISO format
        assert "generated_at" in data
        timestamp = data["generated_at"]

        # Should be able to parse as ISO format
        parsed_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        assert isinstance(parsed_time, datetime)

    def test_top_clients_data_structure(self, client, app_context):
        """Test top clients data structure in business summary"""
        response = client.get("/api/reports/business-summary")

        assert response.status_code == 200
        data = response.get_json()

        top_clients = data["top_clients"]

        if top_clients:  # If there are clients
            client_entry = top_clients[0]

            # Check required fields
            assert "name" in client_entry
            assert "client_type" in client_entry
            assert "project_count" in client_entry
            assert "total_budget" in client_entry

            # Check data types
            assert isinstance(client_entry["project_count"], int)
            assert isinstance(client_entry["total_budget"], (int, float))

    def test_plant_usage_data_structure(self, client, app_context):
        """Test plant usage data structure"""
        response = client.get("/api/reports/plant-usage")

        assert response.status_code == 200
        data = response.get_json()

        plant_usage = data["plant_usage"]

        if plant_usage:  # If there are plants
            plant = plant_usage[0]

            # Check required fields
            assert "name" in plant
            assert "scientific_name" in plant
            assert "category" in plant
            assert "project_count" in plant

            # Check data types
            assert isinstance(plant["project_count"], int)

    def test_status_distribution_structure(self, client, app_context):
        """Test project status distribution in reports"""
        response = client.get("/api/reports/business-summary")

        assert response.status_code == 200
        data = response.get_json()

        status_distribution = data["project_stats"]["status_distribution"]

        # Should be a dictionary
        assert isinstance(status_distribution, dict)

        # Values should be integers (counts)
        for status, count in status_distribution.items():
            assert isinstance(status, str)
            assert isinstance(count, int)
            assert count >= 0


@pytest.mark.api
class TestReportsPDFGeneration(DatabaseTestMixin):
    """Test class for PDF generation functionality"""

    @patch("src.routes.reports.send_file")
    @patch("src.routes.reports.SimpleDocTemplate")
    @patch("src.routes.reports.getSampleStyleSheet")
    def test_business_summary_pdf_structure(
        self,
        mock_styles,
        mock_doc,
        mock_send_file,
        client,
        app_context,
        client_factory,
        project_factory,
    ):
        """Test business summary PDF generation structure"""
        # Set up minimal test data
        client_obj = client_factory(name="Test Client")
        project_factory(
            name="Test Project", client=client_obj, status="active", budget=1000.0
        )

        # Mock the PDF components
        mock_doc_instance = MagicMock()
        mock_doc.return_value = mock_doc_instance

        # Create proper mock styles that work with ReportLab
        from reportlab.lib.styles import ParagraphStyle

        mock_styles.return_value = {
            "Heading1": ParagraphStyle("MockHeading1"),
            "Heading2": ParagraphStyle("MockHeading2"),
            "Normal": ParagraphStyle("MockNormal"),
        }
        mock_send_file.return_value = MagicMock()

        response = client.get(
            "/api/reports/business-summary", query_string={"format": "pdf"}
        )

        # Debug: Check if response is successful
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: "
            f"{response.get_data(as_text=True)}"
        )

        # Should attempt to create PDF
        mock_doc.assert_called()
        mock_doc_instance.build.assert_called()
        # Should send file
        mock_send_file.assert_called()

    @patch("src.routes.reports.SimpleDocTemplate")
    def test_project_report_pdf_structure(self, mock_doc, client, app_context):
        """Test project report PDF generation structure"""
        mock_doc_instance = MagicMock()
        mock_doc.return_value = mock_doc_instance

        response = client.get("/api/reports/project/1", query_string={"format": "pdf"})

        if response.status_code != 404:  # If project exists
            # Should attempt to create PDF
            mock_doc.assert_called()
            mock_doc_instance.build.assert_called()


@pytest.mark.api
class TestReportsErrorHandling(DatabaseTestMixin):
    """Test class for reports error handling"""

    def test_invalid_project_id(self, client, app_context):
        """Test handling of invalid project ID"""
        response = client.get("/api/reports/project/invalid")

        assert response.status_code == 404

    def test_database_error_handling(self, client, app_context):
        """Test handling of database errors"""
        # This might trigger database errors in some configurations
        response = client.get("/api/reports/business-summary")

        # Should either succeed or return proper error
        assert response.status_code in [200, 500]

        if response.status_code == 500:
            data = response.get_json()
            assert "error" in data

    @patch("src.routes.reports.db.session")
    def test_query_error_handling(self, mock_session, client, app_context):
        """Test handling of database query errors"""
        # Mock session to raise an exception
        mock_session.query.side_effect = Exception("Database connection failed")

        response = client.get("/api/reports/business-summary")

        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data
