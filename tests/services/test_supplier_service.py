"""
Test Supplier Service

Comprehensive tests for supplier service layer business logic.
"""

import pytest

from src.models.landscape import Product, Supplier
from src.models.user import db
from src.services.supplier_service import SupplierService
from tests.fixtures.database import DatabaseTestMixin


@pytest.mark.service
class TestSupplierService(DatabaseTestMixin):
    """Test Supplier Service operations"""

    def test_get_all_suppliers_empty(self, app_context):
        """Test getting suppliers when database is empty"""
        result = SupplierService.get_all_suppliers()

        assert result["suppliers"] == []
        assert result["total"] == 0
        assert result["pages"] == 0
        assert result["current_page"] == 1

    def test_get_all_suppliers_with_data(self, app_context, supplier_factory):
        """Test getting suppliers with sample data"""
        supplier1 = supplier_factory(name="Supplier One")  # noqa: F841
        supplier2 = supplier_factory(name="Supplier Two")  # noqa: F841

        result = SupplierService.get_all_suppliers()

        assert len(result["suppliers"]) == 2
        assert result["total"] == 2
        assert result["pages"] == 1
        assert all("id" in supplier for supplier in result["suppliers"])
        assert all("name" in supplier for supplier in result["suppliers"])

    def test_get_all_suppliers_with_search(self, app_context, supplier_factory):
        """Test getting suppliers with search filter"""
        supplier1 = supplier_factory(  # noqa: F841
            name="Alpha Nursery",
            contact_person="John Doe",
            email="contact@alpha.com",
            city="Springfield",
        )
        supplier2 = supplier_factory(  # noqa: F841
            name="Beta Plants",
            contact_person="Jane Smith",
            email="info@beta.com",
            city="Riverside",
        )

        # Search by name
        result = SupplierService.get_all_suppliers(search="Alpha")
        assert len(result["suppliers"]) == 1
        assert result["suppliers"][0]["name"] == "Alpha Nursery"

        # Search by contact person
        result = SupplierService.get_all_suppliers(search="Jane")
        assert len(result["suppliers"]) == 1
        assert result["suppliers"][0]["name"] == "Beta Plants"

        # Search by email
        result = SupplierService.get_all_suppliers(search="alpha.com")
        assert len(result["suppliers"]) == 1
        assert result["suppliers"][0]["name"] == "Alpha Nursery"

        # Search by city
        result = SupplierService.get_all_suppliers(search="Springfield")
        assert len(result["suppliers"]) == 1
        assert result["suppliers"][0]["name"] == "Alpha Nursery"

    def test_get_all_suppliers_with_specialization_filter(self, app_context, supplier_factory):
        """Test getting suppliers with specialization filter"""
        supplier1 = supplier_factory(specialization="Native Plants")  # noqa: F841
        supplier2 = supplier_factory(specialization="Garden Tools")  # noqa: F841
        supplier3 = supplier_factory(specialization="Native Plants")  # noqa: F841

        result = SupplierService.get_all_suppliers(specialization="Native Plants")
        assert len(result["suppliers"]) == 2
        assert all("Native Plants" in supplier["specialization"] for supplier in result["suppliers"])

    def test_get_all_suppliers_pagination(self, app_context, supplier_factory):
        """Test suppliers pagination"""
        # Create 25 suppliers
        for i in range(25):
            supplier_factory(name=f"Supplier {i}")

        # Test first page
        result = SupplierService.get_all_suppliers(page=1, per_page=10)
        assert len(result["suppliers"]) == 10
        assert result["total"] == 25
        assert result["pages"] == 3
        assert result["current_page"] == 1

        # Test second page
        result = SupplierService.get_all_suppliers(page=2, per_page=10)
        assert len(result["suppliers"]) == 10
        assert result["current_page"] == 2

    def test_get_supplier_by_id_success(self, app_context, sample_supplier):
        """Test getting supplier by ID successfully"""
        supplier = SupplierService.get_supplier_by_id(sample_supplier.id)
        assert supplier is not None
        assert supplier.id == sample_supplier.id
        assert supplier.name == sample_supplier.name

    def test_get_supplier_by_id_not_found(self, app_context):
        """Test getting supplier by non-existent ID"""
        supplier = SupplierService.get_supplier_by_id(999)
        assert supplier is None

    def test_create_supplier_success(self, app_context):
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
        }

        supplier = SupplierService.create_supplier(supplier_data)

        assert supplier.id is not None
        assert supplier.name == "Test Supplier"
        assert supplier.contact_person == "John Doe"
        assert supplier.email == "test@supplier.com"
        assert supplier.specialization == "Native Plants"

        # Verify it's in the database
        self.assert_record_count(Supplier, 1)

    def test_create_supplier_minimal_data(self, app_context):
        """Test creating supplier with minimal required data"""
        supplier_data = {"name": "Minimal Supplier"}

        supplier = SupplierService.create_supplier(supplier_data)

        assert supplier.id is not None
        assert supplier.name == "Minimal Supplier"

    def test_update_supplier_success(self, app_context, sample_supplier):
        """Test updating a supplier successfully"""
        update_data = {
            "name": "Updated Supplier Name",
            "email": "updated@supplier.com",
            "specialization": "Garden Equipment",
        }

        updated_supplier = SupplierService.update_supplier(sample_supplier.id, update_data)

        assert updated_supplier is not None
        assert updated_supplier.name == "Updated Supplier Name"
        assert updated_supplier.email == "updated@supplier.com"
        assert updated_supplier.specialization == "Garden Equipment"
        assert updated_supplier.id == sample_supplier.id

    def test_update_supplier_not_found(self, app_context):
        """Test updating non-existent supplier"""
        update_data = {"name": "Updated Name"}
        result = SupplierService.update_supplier(999, update_data)
        assert result is None

    def test_delete_supplier_success(self, app_context, sample_supplier):
        """Test deleting a supplier successfully"""
        supplier_id = sample_supplier.id

        result = SupplierService.delete_supplier(supplier_id)

        assert result is True
        self.assert_record_count(Supplier, 0)

        # Verify supplier is gone
        deleted_supplier = db.session.get(Supplier, supplier_id)
        assert deleted_supplier is None

    def test_delete_supplier_with_products(self, app_context, sample_supplier, product_factory):
        """Test deleting supplier with products should fail"""
        # Add product to supplier
        product_factory(supplier=sample_supplier)

        result = SupplierService.delete_supplier(sample_supplier.id)

        assert result is False
        # Supplier should still exist
        self.assert_record_count(Supplier, 1)

    def test_delete_supplier_with_plants(self, app_context, sample_supplier, plant_factory):
        """Test deleting supplier with plants should fail"""
        # Add plant to supplier
        plant_factory(supplier=sample_supplier)

        result = SupplierService.delete_supplier(sample_supplier.id)

        assert result is False
        # Supplier should still exist
        self.assert_record_count(Supplier, 1)

    def test_delete_supplier_not_found(self, app_context):
        """Test deleting non-existent supplier"""
        result = SupplierService.delete_supplier(999)
        assert result is False

    def test_get_supplier_products(self, app_context, sample_supplier, product_factory):
        """Test getting products for a supplier"""
        product_factory(supplier=sample_supplier, name="Product 1")  # noqa: F841  # noqa: F841
        product_factory(supplier=sample_supplier, name="Product 2")  # noqa: F841  # noqa: F841
        other_supplier = product_factory().supplier
        product_factory(supplier=other_supplier, name="Product 3")  # noqa: F841  # noqa: F841

        supplier_products = SupplierService.get_supplier_products(sample_supplier.id)

        assert len(supplier_products) == 2
        product_names = [product.name for product in supplier_products]
        assert "Product 1" in product_names
        assert "Product 2" in product_names
        assert "Product 3" not in product_names

    def test_get_supplier_plants(self, app_context, sample_supplier, plant_factory):
        """Test getting plants for a supplier"""
        plant1 = plant_factory(supplier=sample_supplier, name="Plant 1")  # noqa: F841
        plant2 = plant_factory(supplier=sample_supplier, name="Plant 2")  # noqa: F841
        other_supplier = plant_factory().supplier
        plant3 = plant_factory(supplier=other_supplier, name="Plant 3")  # noqa: F841

        supplier_plants = SupplierService.get_supplier_plants(sample_supplier.id)

        assert len(supplier_plants) == 2
        plant_names = [plant.name for plant in supplier_plants]
        assert "Plant 1" in plant_names
        assert "Plant 2" in plant_names
        assert "Plant 3" not in plant_names

    def test_get_supplier_statistics(self, app_context, sample_supplier, product_factory, plant_factory):
        """Test getting statistical information for a supplier"""
        # Create products and plants with different prices and quantities
        product_factory(supplier=sample_supplier, price=10.0, stock_quantity=5)
        product_factory(supplier=sample_supplier, price=20.0, stock_quantity=3)
        plant_factory(supplier=sample_supplier, price=15.0)
        plant_factory(supplier=sample_supplier, price=25.0)

        stats = SupplierService.get_supplier_statistics(sample_supplier.id)

        assert stats["supplier_id"] == sample_supplier.id
        assert stats["supplier_name"] == sample_supplier.name
        assert stats["total_products"] == 2
        assert stats["total_plants"] == 2
        assert stats["total_inventory_value"] == 110.0  # (10*5) + (20*3)
        assert stats["average_product_price"] == 15.0  # (10+20)/2
        assert stats["average_plant_price"] == 20.0  # (15+25)/2

    def test_get_supplier_statistics_no_items(self, app_context, sample_supplier):
        """Test getting statistics for supplier with no products/plants"""
        stats = SupplierService.get_supplier_statistics(sample_supplier.id)

        assert stats["total_products"] == 0
        assert stats["total_plants"] == 0
        assert stats["average_product_price"] == 0
        assert stats["average_plant_price"] == 0

    def test_get_supplier_statistics_not_found(self, app_context):
        """Test getting statistics for non-existent supplier"""
        stats = SupplierService.get_supplier_statistics(999)
        assert stats == {}

    def test_search_suppliers(self, app_context, supplier_factory):
        """Test searching suppliers"""
        supplier1 = supplier_factory(  # noqa: F841
            name="Alpha Nursery",
            contact_person="John Alpha",
            email="alpha@nursery.com",
            city="Alphaville",
        )  # noqa: F841
        supplier2 = supplier_factory(  # noqa: F841
            name="Beta Plants",
            contact_person="Beta Manager",
            email="beta@test.com",
            city="Betatown",
        )  # noqa: F841
        supplier3 = supplier_factory(  # noqa: F841
            name="Gamma Gardens",
            contact_person="Gamma Owner",
            email="gamma@gardens.com",
            city="Springfield",
        )  # noqa: F841

        # Search by name
        results = SupplierService.search_suppliers("Alpha")
        assert len(results) == 1
        assert results[0].name == "Alpha Nursery"

        # Search by contact person
        results = SupplierService.search_suppliers("John")
        assert len(results) == 1
        assert results[0].name == "Alpha Nursery"

        # Search by email
        results = SupplierService.search_suppliers("beta@test")
        assert len(results) == 1
        assert results[0].name == "Beta Plants"

    def test_get_suppliers_by_specialization(self, app_context, supplier_factory):
        """Test getting suppliers by specialization"""
        supplier1 = supplier_factory(specialization="Native Plants")  # noqa: F841
        supplier2 = supplier_factory(specialization="Garden Tools")  # noqa: F841
        supplier_factory(specialization="Native Plants and Trees")  # noqa: F841  # noqa: F841

        native_suppliers = SupplierService.get_suppliers_by_specialization("Native Plants")
        assert len(native_suppliers) == 2  # Includes partial matches

    def test_get_supplier_specializations(self, app_context, supplier_factory):
        """Test getting unique supplier specializations"""
        supplier_factory(specialization="Native Plants")
        supplier_factory(specialization="Garden Tools")
        supplier_factory(specialization="Native Plants")  # Duplicate
        supplier_factory(specialization="Landscaping Equipment")
        supplier_factory(specialization=None)  # Should be excluded

        specializations = SupplierService.get_supplier_specializations()
        assert len(specializations) == 3
        assert "Native Plants" in specializations
        assert "Garden Tools" in specializations
        assert "Landscaping Equipment" in specializations

    def test_validate_supplier_data_success(self, app_context):
        """Test validating correct supplier data"""
        valid_data = {
            "name": "Valid Supplier",
            "email": "valid@supplier.com",
            "phone": "555-123-4567",
            "website": "https://validsupplier.com",
        }

        errors = SupplierService.validate_supplier_data(valid_data)
        assert errors == []

    def test_validate_supplier_data_missing_required(self, app_context):
        """Test validating supplier data with missing required fields"""
        invalid_data = {}

        errors = SupplierService.validate_supplier_data(invalid_data)
        assert "name is required" in errors

    def test_validate_supplier_data_invalid_email(self, app_context):
        """Test validating supplier data with invalid email"""
        invalid_data = {"name": "Test Supplier", "email": "invalid-email-format"}

        errors = SupplierService.validate_supplier_data(invalid_data)
        assert "Invalid email format" in errors

    def test_validate_supplier_data_duplicate_email(self, app_context, sample_supplier):
        """Test validating supplier data with duplicate email"""
        invalid_data = {"name": "New Supplier", "email": sample_supplier.email}

        errors = SupplierService.validate_supplier_data(invalid_data)
        assert "Email already exists" in errors

    def test_validate_supplier_data_invalid_phone(self, app_context):
        """Test validating supplier data with invalid phone number"""
        invalid_data = {"name": "Test Supplier", "phone": "not-a-phone-number"}

        errors = SupplierService.validate_supplier_data(invalid_data)
        assert "Invalid phone number format" in errors

    def test_validate_supplier_data_invalid_website(self, app_context):
        """Test validating supplier data with invalid website URL"""
        invalid_data = {"name": "Test Supplier", "website": "invalid-website-url"}

        errors = SupplierService.validate_supplier_data(invalid_data)
        assert "Website must start with http:// or https://" in errors

    def test_add_product_to_supplier(self, app_context, sample_supplier):
        """Test adding a product to a supplier"""
        product_data = {
            "name": "Test Product",
            "category": "Tools",
            "price": 25.99,
            "sku": "TEST001",
        }

        product = SupplierService.add_product_to_supplier(sample_supplier.id, product_data)

        assert product is not None
        assert product.name == "Test Product"
        assert product.supplier_id == sample_supplier.id

        # Verify it's in the database
        self.assert_record_count(Product, 1)

    def test_add_product_to_supplier_not_found(self, app_context):
        """Test adding product to non-existent supplier"""
        product_data = {"name": "Test Product"}
        result = SupplierService.add_product_to_supplier(999, product_data)
        assert result is None

    def test_get_top_suppliers_by_products(self, app_context, supplier_factory, product_factory, plant_factory):
        """Test getting top suppliers by number of products/plants"""
        supplier1 = supplier_factory(name="Supplier 1")
        supplier2 = supplier_factory(name="Supplier 2")
        supplier3 = supplier_factory(name="Supplier 3")

        # Supplier 1: 3 products + 2 plants = 5 total
        for _ in range(3):
            product_factory(supplier=supplier1)
        for _ in range(2):
            plant_factory(supplier=supplier1)

        # Supplier 2: 2 products + 1 plant = 3 total
        for _ in range(2):
            product_factory(supplier=supplier2)
        plant_factory(supplier=supplier2)

        # Supplier 3: 1 product = 1 total
        product_factory(supplier=supplier3)

        top_suppliers = SupplierService.get_top_suppliers_by_products(limit=2)

        assert len(top_suppliers) == 2
        assert top_suppliers[0]["supplier"]["name"] == "Supplier 1"
        assert top_suppliers[0]["total_items"] == 5
        assert top_suppliers[1]["supplier"]["name"] == "Supplier 2"
        assert top_suppliers[1]["total_items"] == 3

    def test_get_supplier_contact_info(self, app_context, sample_supplier):
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

        contact_info = SupplierService.get_supplier_contact_info(sample_supplier.id)

        assert contact_info["name"] == sample_supplier.name
        assert contact_info["contact_person"] == "John Doe"
        assert contact_info["email"] == "john@supplier.com"
        assert contact_info["phone"] == "555-123-4567"
        assert contact_info["website"] == "https://supplier.com"
        assert contact_info["full_address"] == "123 Supplier St, Supplier City 12345"

    def test_get_supplier_contact_info_not_found(self, app_context):
        """Test getting contact info for non-existent supplier"""
        contact_info = SupplierService.get_supplier_contact_info(999)
        assert contact_info == {}


@pytest.mark.integration
class TestSupplierServiceIntegration(DatabaseTestMixin):
    """Integration tests for Supplier Service"""

    def test_full_supplier_lifecycle(self, app_context, product_factory, plant_factory):
        """Test complete supplier lifecycle from creation to deletion"""
        # Create supplier
        supplier_data = {
            "name": "Lifecycle Test Supplier",
            "contact_person": "Test Contact",
            "email": "lifecycle@supplier.com",
            "phone": "555-LIFECYCLE",
            "specialization": "Testing Equipment",
        }

        supplier = SupplierService.create_supplier(supplier_data)
        assert supplier.id is not None

        # Add products and plants
        product = SupplierService.add_product_to_supplier(supplier.id, {"name": "Test Product", "price": 25.0})
        plant = plant_factory(supplier=supplier, price=15.0)

        # Get supplier statistics
        stats = SupplierService.get_supplier_statistics(supplier.id)
        assert stats["total_products"] == 1
        assert stats["total_plants"] == 1

        # Search for supplier
        search_results = SupplierService.search_suppliers("Lifecycle")
        assert len(search_results) == 1
        assert search_results[0].id == supplier.id

        # Update supplier
        update_data = {
            "email": "updated@supplier.com",
            "specialization": "Updated Equipment",
        }
        updated_supplier = SupplierService.update_supplier(supplier.id, update_data)
        assert updated_supplier.email == "updated@supplier.com"

        # Try to delete supplier (should fail due to products/plants)
        delete_result = SupplierService.delete_supplier(supplier.id)
        assert delete_result is False

        # Remove products and plants, then delete
        db.session.delete(product)
        db.session.delete(plant)
        db.session.commit()

        delete_result = SupplierService.delete_supplier(supplier.id)
        assert delete_result is True

        # Verify deletion
        deleted_supplier = SupplierService.get_supplier_by_id(supplier.id)
        assert deleted_supplier is None

    def test_supplier_product_plant_management(self, app_context, supplier_factory, product_factory, plant_factory):
        """Test complex supplier-product-plant relationship scenarios"""
        supplier = supplier_factory(name="Management Test Supplier")

        # Add diverse products
        products = [  # noqa: F841
            product_factory(
                supplier=supplier,
                name=f"Product {i}",
                price=float(i * 10),
                stock_quantity=i,
            )
            for i in range(1, 4)
        ]

        # Add diverse plants
        plants = [  # noqa: F841
            plant_factory(supplier=supplier, name=f"Plant {i}", price=float(i * 5)) for i in range(1, 3)
        ]

        # Test supplier products retrieval
        supplier_products = SupplierService.get_supplier_products(supplier.id)
        assert len(supplier_products) == 3

        # Test supplier plants retrieval
        supplier_plants = SupplierService.get_supplier_plants(supplier.id)
        assert len(supplier_plants) == 2

        # Test supplier statistics
        stats = SupplierService.get_supplier_statistics(supplier.id)
        assert stats["total_products"] == 3
        assert stats["total_plants"] == 2

        # Calculate expected inventory value: (10*1) + (20*2) + (30*3) = 140
        expected_inventory_value = 10 * 1 + 20 * 2 + 30 * 3
        assert stats["total_inventory_value"] == expected_inventory_value

        # Test top suppliers ranking
        top_suppliers = SupplierService.get_top_suppliers_by_products(limit=5)
        supplier_entry = next((s for s in top_suppliers if s["supplier"]["id"] == supplier.id), None)
        assert supplier_entry is not None
        assert supplier_entry["total_items"] == 5  # 3 products + 2 plants

    def test_supplier_search_and_filtering_complex(self, app_context, supplier_factory):
        """Test complex search and filtering scenarios"""
        # Create diverse suppliers
        suppliers_data = [
            {
                "name": "Alpha Plant Nursery",
                "specialization": "Native Plants",
                "contact_person": "Alice Alpha",
                "city": "Springfield",
            },
            {
                "name": "Beta Garden Tools",
                "specialization": "Garden Equipment",
                "contact_person": "Bob Beta",
                "city": "Riverside",
            },
            {
                "name": "Gamma Native Plants",
                "specialization": "Native Plants",
                "contact_person": "Carol Gamma",
                "city": "Springfield",
            },
        ]

        for data in suppliers_data:
            supplier_factory(**data)

        # Test search by specialization
        native_suppliers = SupplierService.get_all_suppliers(specialization="Native Plants")
        assert len(native_suppliers["suppliers"]) == 2

        # Test search by city
        springfield_suppliers = SupplierService.get_all_suppliers(search="Springfield")
        assert len(springfield_suppliers["suppliers"]) == 2

        # Test search by contact person
        alice_suppliers = SupplierService.get_all_suppliers(search="Alice")
        assert len(alice_suppliers["suppliers"]) == 1
        assert alice_suppliers["suppliers"][0]["name"] == "Alpha Plant Nursery"

        # Test suppliers by specialization method
        native_only = SupplierService.get_suppliers_by_specialization("Native Plants")
        assert len(native_only) == 2

        # Test specializations list
        specializations = SupplierService.get_supplier_specializations()
        assert "Native Plants" in specializations
        assert "Garden Equipment" in specializations
