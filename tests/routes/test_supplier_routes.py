"""
Test Supplier Routes

Comprehensive tests for supplier API endpoints.
"""

import json

import pytest

from src.models.landscape import Plant, Product, Supplier
from src.models.user import db
from tests.fixtures.database import DatabaseTestMixin


@pytest.mark.api
class TestSupplierRoutes(DatabaseTestMixin):
    """Test Supplier API endpoints"""

    def test_get_suppliers_empty(self, client, app_context):
        """Test getting suppliers when database is empty"""
        response = client.get("/api/suppliers")

        assert response.status_code == 200
        data = response.get_json()
        assert data["suppliers"] == []
        assert data["total"] == 0

    def test_get_suppliers_with_data(self, client, app_context, supplier_factory):
        """Test getting suppliers with sample data"""
        suppliers = [supplier_factory() for _ in range(3)]  # noqa: F841

        response = client.get("/api/suppliers")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["suppliers"]) == 3
        assert data["total"] == 3
        assert all("id" in supplier for supplier in data["suppliers"])
        assert all("name" in supplier for supplier in data["suppliers"])

    def test_get_suppliers_with_search(self, client, app_context, supplier_factory):
        """Test getting suppliers with search parameter"""
        supplier1 = supplier_factory(  # noqa: F841
            name="Alpha Nursery", contact_person="John Alpha"
        )  # noqa: F841
        supplier2 = supplier_factory(  # noqa: F841
            name="Beta Plants", city="Springfield", contact_person="Bob Springfield"
        )  # noqa: F841
        supplier3 = supplier_factory(  # noqa: F841
            name="Gamma Gardens", email="info@gamma.com", contact_person="Charlie Gamma"
        )  # noqa: F841

        # Search by name
        response = client.get("/api/suppliers?search=Alpha")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["suppliers"]) == 1
        assert data["suppliers"][0]["name"] == "Alpha Nursery"

        # Search by contact person
        response = client.get("/api/suppliers?search=John")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["suppliers"]) == 1
        assert data["suppliers"][0]["name"] == "Alpha Nursery"

        # Search by city
        response = client.get("/api/suppliers?search=Springfield")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["suppliers"]) == 1
        assert data["suppliers"][0]["name"] == "Beta Plants"

    def test_get_suppliers_pagination(self, client, app_context, supplier_factory):
        """Test suppliers pagination"""
        # Create 15 suppliers
        for i in range(15):
            supplier_factory(name=f"Supplier {i}")

        # Test first page
        response = client.get("/api/suppliers?page=1&per_page=10")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["suppliers"]) == 10
        assert data["total"] == 15
        assert data["pages"] == 2
        assert data["current_page"] == 1

        # Test second page
        response = client.get("/api/suppliers?page=2&per_page=10")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["suppliers"]) == 5
        assert data["current_page"] == 2

    def test_create_supplier_success(self, client, app_context):
        """Test creating a supplier successfully"""
        supplier_data = {
            "name": "Test Supplier",
            "contact_person": "John Doe",
            "email": "test@supplier.com",
            "phone": "555-123-4567",
            "address": "123 Supplier Street",
            "city": "Supplier City",
            "postal_code": "12345",
            "specialization": "Native Plants",
            "website": "https://testsupplier.com",
            "notes": "Test supplier notes",
        }

        response = client.post(
            "/api/suppliers",
            data=json.dumps(supplier_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "Test Supplier"
        assert data["contact_person"] == "John Doe"
        assert data["email"] == "test@supplier.com"
        assert data["specialization"] == "Native Plants"

        # Verify in database
        self.assert_record_count(Supplier, 1)

    def test_create_supplier_minimal_data(self, client, app_context):
        """Test creating supplier with minimal required data"""
        supplier_data = {"name": "Minimal Supplier"}

        response = client.post(
            "/api/suppliers",
            data=json.dumps(supplier_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "Minimal Supplier"

    def test_create_supplier_missing_required_fields(self, client, app_context):
        """Test creating supplier with missing required fields"""
        supplier_data = {"contact_person": "John Doe"}

        response = client.post(
            "/api/suppliers",
            data=json.dumps(supplier_data),
            content_type="application/json",
        )

        assert response.status_code == 422
        data = response.get_json()
        assert "error" in data

    def test_create_supplier_invalid_email(self, client, app_context):
        """Test creating supplier with invalid email"""
        supplier_data = {"name": "Test Supplier", "email": "invalid-email-format"}

        response = client.post(
            "/api/suppliers",
            data=json.dumps(supplier_data),
            content_type="application/json",
        )

        assert response.status_code == 422
        data = response.get_json()
        assert "validation_errors" in data

    def test_create_supplier_duplicate_email(
        self, client, app_context, sample_supplier
    ):
        """Test creating supplier with duplicate email"""
        supplier_data = {
            "name": "Duplicate Email Supplier",
            "email": sample_supplier.email,
        }

        response = client.post(
            "/api/suppliers",
            data=json.dumps(supplier_data),
            content_type="application/json",
        )

        assert response.status_code == 422
        data = response.get_json()
        assert "validation_errors" in data
        assert any("email" in error.lower() for error in data["validation_errors"])

    def test_get_supplier_by_id_success(self, client, app_context, sample_supplier):
        """Test getting a specific supplier by ID"""
        response = client.get(f"/api/suppliers/{sample_supplier.id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == sample_supplier.id
        assert data["name"] == sample_supplier.name

    def test_get_supplier_by_id_not_found(self, client, app_context):
        """Test getting supplier by non-existent ID"""
        response = client.get("/api/suppliers/999")

        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data

    def test_update_supplier_success(self, client, app_context, sample_supplier):
        """Test updating a supplier successfully"""
        update_data = {
            "name": "Updated Supplier Name",
            "email": "updated@supplier.com",
            "specialization": "Garden Equipment",
            "notes": "Updated notes",
        }

        response = client.put(
            f"/api/suppliers/{sample_supplier.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "Updated Supplier Name"
        assert data["email"] == "updated@supplier.com"
        assert data["specialization"] == "Garden Equipment"

    def test_update_supplier_not_found(self, client, app_context):
        """Test updating non-existent supplier"""
        update_data = {"name": "Updated Name"}

        response = client.put(
            "/api/suppliers/999",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data

    def test_update_supplier_invalid_data(self, client, app_context, sample_supplier):
        """Test updating supplier with invalid data"""
        update_data = {"email": "invalid-email-format", "website": "invalid-url"}

        response = client.put(
            f"/api/suppliers/{sample_supplier.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 422
        data = response.get_json()
        assert "validation_errors" in data

    def test_delete_supplier_success(self, client, app_context, sample_supplier):
        """Test deleting a supplier successfully"""
        supplier_id = sample_supplier.id

        response = client.delete(f"/api/suppliers/{supplier_id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Supplier deleted successfully"

        # Verify deletion
        self.assert_record_count(Supplier, 0)

    def test_delete_supplier_not_found(self, client, app_context):
        """Test deleting non-existent supplier"""
        response = client.delete("/api/suppliers/999")

        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data

    def test_delete_supplier_with_products(
        self, client, app_context, sample_supplier, product_factory
    ):
        """Test deleting supplier that has products"""
        product_factory(supplier=sample_supplier)

        response = client.delete(f"/api/suppliers/{sample_supplier.id}")

        # Should fail due to foreign key constraint
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_delete_supplier_with_plants(
        self, client, app_context, sample_supplier, plant_factory
    ):
        """Test deleting supplier that has plants"""
        plant_factory(supplier=sample_supplier)

        response = client.delete(f"/api/suppliers/{sample_supplier.id}")

        # Should fail due to foreign key constraint
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_get_supplier_products(
        self, client, app_context, sample_supplier, product_factory
    ):
        """Test getting products for a specific supplier"""
        product1 = product_factory(  # noqa: F841
            supplier=sample_supplier, name="Product 1"
        )  # noqa: F841
        product2 = product_factory(  # noqa: F841
            supplier=sample_supplier, name="Product 2"
        )  # noqa: F841
        other_supplier = product_factory().supplier
        product3 = product_factory(  # noqa: F841
            supplier=other_supplier, name="Product 3"
        )  # noqa: F841

        response = client.get(f"/api/suppliers/{sample_supplier.id}/products")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["products"]) == 2
        product_names = [product["name"] for product in data["products"]]
        assert "Product 1" in product_names
        assert "Product 2" in product_names
        assert "Product 3" not in product_names

    def test_get_supplier_plants(
        self, client, app_context, sample_supplier, plant_factory
    ):
        """Test getting plants for a specific supplier"""
        plant1 = plant_factory(supplier=sample_supplier, name="Plant 1")  # noqa: F841
        plant2 = plant_factory(supplier=sample_supplier, name="Plant 2")  # noqa: F841
        other_supplier = plant_factory().supplier
        plant3 = plant_factory(supplier=other_supplier, name="Plant 3")  # noqa: F841

        response = client.get(f"/api/suppliers/{sample_supplier.id}/plants")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["plants"]) == 2
        plant_names = [plant["name"] for plant in data["plants"]]
        assert "Plant 1" in plant_names
        assert "Plant 2" in plant_names
        assert "Plant 3" not in plant_names

    def test_get_supplier_statistics(
        self, client, app_context, sample_supplier, product_factory, plant_factory
    ):
        """Test getting statistical information for a supplier"""
        # Create products and plants with different prices and quantities
        product_factory(supplier=sample_supplier, price=10.0, stock_quantity=5)
        product_factory(supplier=sample_supplier, price=20.0, stock_quantity=3)
        plant_factory(supplier=sample_supplier, price=15.0)
        plant_factory(supplier=sample_supplier, price=25.0)

        response = client.get(f"/api/suppliers/{sample_supplier.id}/statistics")

        assert response.status_code == 200
        data = response.get_json()
        assert data["supplier_id"] == sample_supplier.id
        assert data["total_products"] == 2
        assert data["total_plants"] == 2
        assert data["total_inventory_value"] == 110.0  # (10*5) + (20*3)
        assert data["average_product_price"] == 15.0  # (10+20)/2
        assert data["average_plant_price"] == 20.0  # (15+25)/2

    def test_add_product_to_supplier(self, client, app_context, sample_supplier):
        """Test adding a product to a supplier"""
        product_data = {
            "name": "Test Product",
            "category": "Tools",
            "price": 25.99,
            "sku": "TEST001",
            "stock_quantity": 10,
        }

        response = client.post(
            f"/api/suppliers/{sample_supplier.id}/products",
            data=json.dumps(product_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "Test Product"
        assert data["supplier_id"] == sample_supplier.id

        # Verify in database
        self.assert_record_count(Product, 1)

    def test_add_product_to_supplier_not_found(self, client, app_context):
        """Test adding product to non-existent supplier"""
        product_data = {"name": "Test Product"}

        response = client.post(
            "/api/suppliers/999/products",
            data=json.dumps(product_data),
            content_type="application/json",
        )

        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data

    def test_get_supplier_specializations(self, client, app_context, supplier_factory):
        """Test getting unique supplier specializations"""
        supplier_factory(specialization="Native Plants")
        supplier_factory(specialization="Garden Tools")
        supplier_factory(specialization="Native Plants")  # Duplicate
        supplier_factory(specialization="Landscaping Equipment")
        supplier_factory(specialization=None)  # Should be excluded

        response = client.get("/api/suppliers/specializations")

        assert response.status_code == 200
        data = response.get_json()
        assert "specializations" in data
        specializations = data["specializations"]
        assert len(specializations) == 3
        assert "Native Plants" in specializations
        assert "Garden Tools" in specializations
        assert "Landscaping Equipment" in specializations

    def test_search_suppliers_by_specialization(
        self, client, app_context, supplier_factory
    ):
        """Test searching suppliers by specialization"""
        supplier1 = supplier_factory(specialization="Native Plants")  # noqa: F841
        supplier2 = supplier_factory(specialization="Garden Tools")  # noqa: F841
        supplier3 = supplier_factory(  # noqa: F841
            specialization="Native Plants and Trees"
        )  # noqa: F841

        response = client.get("/api/suppliers?specialization=Native Plants")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["suppliers"]) == 2  # Includes partial matches

    def test_get_top_suppliers(
        self, client, app_context, supplier_factory, product_factory, plant_factory
    ):
        """Test getting top suppliers by products/plants"""
        supplier1 = supplier_factory(name="Supplier 1")
        supplier2 = supplier_factory(name="Supplier 2")

        # Supplier 1: 3 products + 2 plants = 5 total
        for _ in range(3):
            product_factory(supplier=supplier1)
        for _ in range(2):
            plant_factory(supplier=supplier1)

        # Supplier 2: 1 product = 1 total
        product_factory(supplier=supplier2)

        response = client.get("/api/suppliers/top?limit=5")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["suppliers"]) == 2
        assert data["suppliers"][0]["supplier"]["name"] == "Supplier 1"
        assert data["suppliers"][0]["total_items"] == 5

    def test_supplier_contact_info(self, client, app_context, sample_supplier):
        """Test getting formatted contact information for a supplier"""
        # Update supplier with complete contact info
        sample_supplier.contact_person = "John Doe"
        sample_supplier.email = "john@supplier.com"
        sample_supplier.phone = "555-123-4567"
        sample_supplier.address = "123 Supplier St"
        sample_supplier.city = "Supplier City"
        sample_supplier.postal_code = "12345"
        sample_supplier.website = "https://supplier.com"
        db.session.commit()

        response = client.get(f"/api/suppliers/{sample_supplier.id}/contact")

        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == sample_supplier.name
        assert data["contact_person"] == "John Doe"
        assert data["email"] == "john@supplier.com"
        assert data["full_address"] == "123 Supplier St, Supplier City 12345"

    def test_suppliers_bulk_operations(self, client, app_context):
        """Test bulk supplier operations"""
        suppliers_data = {
            "suppliers": [
                {"name": "Bulk Supplier 1", "specialization": "Native Plants"},
                {"name": "Bulk Supplier 2", "specialization": "Garden Tools"},
            ]
        }

        response = client.post(
            "/api/suppliers/bulk-import",
            data=json.dumps(suppliers_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["imported_count"] == 2

        # Verify in database
        self.assert_record_count(Supplier, 2)

    def test_suppliers_export(self, client, app_context, supplier_factory):
        """Test exporting suppliers data"""
        suppliers = [supplier_factory() for _ in range(3)]  # noqa: F841

        response = client.get("/api/suppliers/export?format=json")

        assert response.status_code == 200
        data = response.get_json()
        assert "suppliers" in data
        assert len(data["suppliers"]) == 3


@pytest.mark.integration
class TestSupplierRoutesIntegration(DatabaseTestMixin):
    """Integration tests for Supplier API endpoints"""

    def test_full_supplier_api_workflow(self, client, app_context):
        """Test complete supplier API workflow"""
        # 1. Create supplier
        supplier_data = {
            "name": "Workflow Test Supplier",
            "contact_person": "Test Contact",
            "email": "workflow@supplier.com",
            "phone": "555-123-4567",
            "specialization": "Testing Equipment",
        }

        response = client.post(
            "/api/suppliers",
            data=json.dumps(supplier_data),
            content_type="application/json",
        )
        assert response.status_code == 201
        created_supplier = response.get_json()
        supplier_id = created_supplier["id"]

        # 2. Get supplier by ID
        response = client.get(f"/api/suppliers/{supplier_id}")
        assert response.status_code == 200
        retrieved_supplier = response.get_json()
        assert retrieved_supplier["name"] == "Workflow Test Supplier"

        # 3. Add product to supplier
        product_data = {"name": "Test Product", "price": 25.0, "category": "Tools"}
        response = client.post(
            f"/api/suppliers/{supplier_id}/products",
            data=json.dumps(product_data),
            content_type="application/json",
        )
        assert response.status_code == 201

        # 4. Get supplier products
        response = client.get(f"/api/suppliers/{supplier_id}/products")
        assert response.status_code == 200
        products_data = response.get_json()
        assert len(products_data["products"]) == 1

        # 5. Get supplier statistics
        response = client.get(f"/api/suppliers/{supplier_id}/statistics")
        assert response.status_code == 200
        stats_data = response.get_json()
        assert stats_data["total_products"] == 1

        # 6. Update supplier
        update_data = {"email": "updated@supplier.com"}
        response = client.put(
            f"/api/suppliers/{supplier_id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )
        assert response.status_code == 200
        updated_supplier = response.get_json()
        assert updated_supplier["email"] == "updated@supplier.com"

        # 7. Search for supplier
        response = client.get("/api/suppliers?search=Workflow")
        assert response.status_code == 200
        search_results = response.get_json()
        assert len(search_results["suppliers"]) == 1

        # Note: Cannot delete supplier due to product constraint
        # This demonstrates referential integrity

    def test_supplier_filtering_and_search_combinations(
        self, client, app_context, supplier_factory
    ):
        """Test various combinations of supplier filters and search"""
        # Create diverse suppliers
        suppliers = [  # noqa: F841
            supplier_factory(
                name="Alpha Native Plants",
                specialization="Native Plants",
                city="Springfield",
                contact_person="Alice Alpha",
            ),
            supplier_factory(
                name="Beta Garden Tools",
                specialization="Garden Equipment",
                city="Riverside",
                contact_person="Bob Beta",
            ),
            supplier_factory(
                name="Gamma Native Nursery",
                specialization="Native Plants",
                city="Springfield",
                contact_person="Carol Gamma",
            ),
        ]

        # Test specialization filter
        response = client.get("/api/suppliers?specialization=Native Plants")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["suppliers"]) == 2

        # Test search by city
        response = client.get("/api/suppliers?search=Springfield")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["suppliers"]) == 2

        # Test search by contact person
        response = client.get("/api/suppliers?search=Alice")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["suppliers"]) == 1
        assert data["suppliers"][0]["name"] == "Alpha Native Plants"

    def test_supplier_product_plant_management(
        self, client, app_context, supplier_factory, product_factory, plant_factory
    ):
        """Test managing products and plants for suppliers"""
        supplier = supplier_factory(name="Management Test Supplier")

        # Add products
        for i in range(3):
            product_data = {
                "name": f"Product {i}",
                "price": float(10 + i * 5),
                "stock_quantity": i + 1,
            }
            response = client.post(
                f"/api/suppliers/{supplier.id}/products",
                data=json.dumps(product_data),
                content_type="application/json",
            )
            assert response.status_code == 201

        # Add plants directly via factory (as there might not be an API endpoint)
        plants = [  # noqa: F841
            plant_factory(supplier=supplier, name=f"Plant {i}") for i in range(2)
        ]  # noqa: F841

        # Get supplier products
        response = client.get(f"/api/suppliers/{supplier.id}/products")
        assert response.status_code == 200
        products_data = response.get_json()
        assert len(products_data["products"]) == 3

        # Get supplier plants
        response = client.get(f"/api/suppliers/{supplier.id}/plants")
        assert response.status_code == 200
        plants_data = response.get_json()
        assert len(plants_data["plants"]) == 2

        # Get comprehensive statistics
        response = client.get(f"/api/suppliers/{supplier.id}/statistics")
        assert response.status_code == 200
        stats_data = response.get_json()
        assert stats_data["total_products"] == 3
        assert stats_data["total_plants"] == 2

        # Check top suppliers ranking
        response = client.get("/api/suppliers/top")
        assert response.status_code == 200
        top_data = response.get_json()
        assert len(top_data["suppliers"]) >= 1
        # The test supplier should be in the results
        supplier_found = any(
            s["supplier"]["id"] == supplier.id for s in top_data["suppliers"]
        )
        assert supplier_found

    def test_supplier_validation_comprehensive(
        self, client, app_context, sample_supplier
    ):
        """Test comprehensive supplier validation scenarios"""
        # Test all validation rules

        # Invalid email format
        invalid_data = {"name": "Test Supplier", "email": "invalid-email"}
        response = client.post(
            "/api/suppliers",
            data=json.dumps(invalid_data),
            content_type="application/json",
        )
        assert response.status_code == 422

        # Duplicate email
        duplicate_data = {
            "name": "Duplicate Email Supplier",
            "email": sample_supplier.email,
        }
        response = client.post(
            "/api/suppliers",
            data=json.dumps(duplicate_data),
            content_type="application/json",
        )
        assert response.status_code == 422

        # Invalid phone format
        invalid_phone_data = {"name": "Test Supplier", "phone": "not-a-phone-number"}
        response = client.post(
            "/api/suppliers",
            data=json.dumps(invalid_phone_data),
            content_type="application/json",
        )
        assert response.status_code == 422

        # Invalid website URL
        invalid_website_data = {"name": "Test Supplier", "website": "invalid-url"}
        response = client.post(
            "/api/suppliers",
            data=json.dumps(invalid_website_data),
            content_type="application/json",
        )
        assert response.status_code == 422
