"""
Supplier Service

Handles all supplier-related business logic and database operations.
"""

from datetime import UTC, datetime
from typing import Dict, List, Optional

from sqlalchemy import or_

from src.models.landscape import Plant, Product, Supplier
from src.models.user import db


class SupplierService:
    """Service class for supplier operations"""

    @staticmethod
    def get_all_suppliers(search: str = "", specialization: str = "", page: int = 1, per_page: int = 50) -> Dict:
        """Get all suppliers with optional filtering and pagination"""
        query = Supplier.query

        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Supplier.name.ilike(search_term),
                    Supplier.contact_person.ilike(search_term),
                    Supplier.email.ilike(search_term),
                    Supplier.city.ilike(search_term),
                )
            )

        if specialization:
            query = query.filter(Supplier.specialization.ilike(f"%{specialization}%"))

        # Execute query with pagination
        suppliers = query.order_by(Supplier.name).paginate(page=page, per_page=per_page, error_out=False)

        return {
            "suppliers": [supplier.to_dict() for supplier in suppliers.items],
            "total": suppliers.total,
            "pages": suppliers.pages,
            "current_page": suppliers.page,
            "per_page": suppliers.per_page,
        }

    @staticmethod
    def get_supplier_by_id(supplier_id: int) -> Optional[Supplier]:
        """Get a supplier by ID"""
        return db.session.get(Supplier, supplier_id)

    @staticmethod
    def create_supplier(supplier_data: Dict) -> Supplier:
        """Create a new supplier"""
        supplier = Supplier(**supplier_data)
        db.session.add(supplier)
        db.session.commit()
        return supplier

    @staticmethod
    def update_supplier(supplier_id: int, supplier_data: Dict) -> Optional[Supplier]:
        """Update an existing supplier"""
        supplier = db.session.get(Supplier, supplier_id)
        if not supplier:
            return None

        for key, value in supplier_data.items():
            if hasattr(supplier, key):
                setattr(supplier, key, value)

        supplier.updated_at = datetime.now(UTC)
        db.session.commit()
        return supplier

    @staticmethod
    def delete_supplier(supplier_id: int) -> bool:
        """Delete a supplier"""
        supplier = db.session.get(Supplier, supplier_id)
        if not supplier:
            return False

        # Check if supplier has products or plants
        product_count = Product.query.filter_by(supplier_id=supplier_id).count()
        plant_count = Plant.query.filter_by(supplier_id=supplier_id).count()

        if product_count > 0 or plant_count > 0:
            return False  # Cannot delete supplier with associated products/plants

        db.session.delete(supplier)
        db.session.commit()
        return True

    @staticmethod
    def get_supplier_products(supplier_id: int) -> List[Product]:
        """Get all products for a specific supplier"""
        return Product.query.filter_by(supplier_id=supplier_id).order_by(Product.name).all()

    @staticmethod
    def get_supplier_plants(supplier_id: int) -> List[Plant]:
        """Get all plants for a specific supplier"""
        return Plant.query.filter_by(supplier_id=supplier_id).order_by(Plant.name).all()

    @staticmethod
    def get_supplier_statistics(supplier_id: int) -> Dict:
        """Get statistical information for a supplier"""
        supplier = db.session.get(Supplier, supplier_id)
        if not supplier:
            return {}

        products = Product.query.filter_by(supplier_id=supplier_id).all()
        plants = Plant.query.filter_by(supplier_id=supplier_id).all()

        total_products = len(products)
        total_plants = len(plants)
        total_inventory_value = sum((p.price or 0) * (p.stock_quantity or 0) for p in products)

        average_product_price = sum(p.price or 0 for p in products) / total_products if total_products > 0 else 0
        average_plant_price = sum(p.price or 0 for p in plants) / total_plants if total_plants > 0 else 0

        return {
            "supplier_id": supplier_id,
            "supplier_name": supplier.name,
            "total_products": total_products,
            "total_plants": total_plants,
            "total_inventory_value": total_inventory_value,
            "average_product_price": average_product_price,
            "average_plant_price": average_plant_price,
        }

    @staticmethod
    def search_suppliers(search_term: str) -> List[Supplier]:
        """Search suppliers by name, contact person, email, or city"""
        search_term = f"%{search_term}%"
        return (
            Supplier.query.filter(
                or_(
                    Supplier.name.ilike(search_term),
                    Supplier.contact_person.ilike(search_term),
                    Supplier.email.ilike(search_term),
                    Supplier.city.ilike(search_term),
                )
            )
            .order_by(Supplier.name)
            .all()
        )

    @staticmethod
    def get_suppliers_by_specialization(specialization: str) -> List[Supplier]:
        """Get suppliers by specialization"""
        return Supplier.query.filter(Supplier.specialization.ilike(f"%{specialization}%")).order_by(Supplier.name).all()

    @staticmethod
    def get_supplier_specializations() -> List[str]:
        """Get all unique supplier specializations"""
        specializations = db.session.query(Supplier.specialization).distinct().all()
        return [spec[0] for spec in specializations if spec[0]]

    @staticmethod
    def validate_supplier_data(supplier_data: Dict) -> List[str]:
        """Validate supplier data and return list of validation errors"""
        errors = []

        # Required fields
        required_fields = ["name"]
        for field in required_fields:
            if not supplier_data.get(field):
                errors.append(f"{field} is required")

        # Email validation
        if supplier_data.get("email"):
            email = supplier_data["email"]
            if "@" not in email or "." not in email:
                errors.append("Invalid email format")

            # Check for duplicate email
            existing_supplier = Supplier.query.filter_by(email=email).first()
            if existing_supplier and existing_supplier.id != supplier_data.get("id"):
                errors.append("Email already exists")

        # Phone validation
        if supplier_data.get("phone"):
            phone = supplier_data["phone"].replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            if not phone.replace("+", "").isdigit():
                errors.append("Invalid phone number format")

        # Website validation
        if supplier_data.get("website"):
            website = supplier_data["website"]
            if not (website.startswith("http://") or website.startswith("https://")):
                errors.append("Website must start with http:// or https://")

        return errors

    @staticmethod
    def add_product_to_supplier(supplier_id: int, product_data: Dict) -> Optional[Product]:
        """Add a product to a supplier"""
        supplier = db.session.get(Supplier, supplier_id)
        if not supplier:
            return None

        product_data["supplier_id"] = supplier_id
        product = Product(**product_data)
        db.session.add(product)
        db.session.commit()
        return product

    @staticmethod
    def get_top_suppliers_by_products(limit: int = 10) -> List[Dict]:
        """Get top suppliers by number of products"""
        suppliers = Supplier.query.all()
        supplier_stats = []

        for supplier in suppliers:
            product_count = Product.query.filter_by(supplier_id=supplier.id).count()
            plant_count = Plant.query.filter_by(supplier_id=supplier.id).count()
            total_items = product_count + plant_count

            if total_items > 0:
                supplier_stats.append(
                    {
                        "supplier": supplier.to_dict(),
                        "product_count": product_count,
                        "plant_count": plant_count,
                        "total_items": total_items,
                    }
                )

        # Sort by total items and limit
        supplier_stats.sort(key=lambda x: x["total_items"], reverse=True)
        return supplier_stats[:limit]

    @staticmethod
    def get_supplier_contact_info(supplier_id: int) -> Dict:
        """Get formatted contact information for a supplier"""
        supplier = db.session.get(Supplier, supplier_id)
        if not supplier:
            return {}

        return {
            "name": supplier.name,
            "contact_person": supplier.contact_person,
            "email": supplier.email,
            "phone": supplier.phone,
            "address": supplier.address,
            "city": supplier.city,
            "postal_code": supplier.postal_code,
            "website": supplier.website,
            "full_address": (
                f"{supplier.address}, {supplier.city} {supplier.postal_code}" if supplier.address else None
            ),
        }
