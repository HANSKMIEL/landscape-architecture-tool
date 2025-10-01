from flask import Blueprint, jsonify, request

from src.models.landscape import Supplier
from src.models.user import db
from src.routes.user import data_access_required, login_required

suppliers_bp = Blueprint("suppliers", __name__)


@suppliers_bp.route("/", methods=["GET"])
@login_required
def get_suppliers():
    """Get all suppliers with optional search"""
    try:
        search = request.args.get("search", "")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 50))

        query = Supplier.query

        if search:
            query = query.filter(
                Supplier.name.contains(search)
                | Supplier.contact_person.contains(search)
                | Supplier.city.contains(search)
            )

        suppliers = query.order_by(Supplier.name).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify(
            {
                "suppliers": [supplier.to_dict() for supplier in suppliers.items],
                "total": suppliers.total,
                "pages": suppliers.pages,
                "current_page": page,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@suppliers_bp.route("/", methods=["POST"])
@data_access_required
def create_supplier():
    """Create a new supplier"""
    try:
        data = request.get_json()

        supplier = Supplier(
            name=data.get("name"),
            contact_person=data.get("contact_person"),
            email=data.get("email"),
            phone=data.get("phone"),
            address=data.get("address"),
            city=data.get("city"),
            postal_code=data.get("postal_code"),
            country=data.get("country", "Netherlands"),
            website=data.get("website"),
            notes=data.get("notes"),
        )

        db.session.add(supplier)
        db.session.commit()

        return jsonify(supplier.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@suppliers_bp.route("/<int:supplier_id>", methods=["GET"])
def get_supplier(supplier_id):
    """Get a specific supplier"""
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        return jsonify(supplier.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@suppliers_bp.route("/<int:supplier_id>", methods=["PUT"])
@data_access_required
def update_supplier(supplier_id):
    """Update a supplier"""
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        data = request.get_json()

        for field in [
            "name",
            "contact_person",
            "email",
            "phone",
            "address",
            "city",
            "postal_code",
            "country",
            "website",
            "notes",
        ]:
            if field in data:
                setattr(supplier, field, data[field])

        db.session.commit()
        return jsonify(supplier.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@suppliers_bp.route("/<int:supplier_id>", methods=["DELETE"])
@data_access_required
def delete_supplier(supplier_id):
    """Delete a supplier"""
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        db.session.delete(supplier)
        db.session.commit()
        return jsonify({"message": "Supplier deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
