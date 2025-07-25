# Products API Routes
# File location: src/routes/products.py
# This file handles all product management operations

import io
from datetime import datetime

import pandas as pd
from flask import Blueprint, jsonify, request

from src.models.landscape import Product, Supplier, db

products_bp = Blueprint("products", __name__)


@products_bp.route("/api/products", methods=["GET"])
def get_products():
    """Get all products with optional filtering"""
    try:
        # Get query parameters
        search = request.args.get("search", "")
        category = request.args.get("category", "")
        supplier_id = request.args.get("supplier_id", "")
        in_stock = request.args.get("in_stock", "")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 50))

        # Build query
        query = Product.query.join(
            Supplier, Product.supplier_id == Supplier.id, isouter=True
        )

        # Apply filters
        if search:
            query = query.filter(
                db.or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%"),
                    Product.sku.ilike(f"%{search}%"),
                )
            )

        if category:
            query = query.filter(Product.category == category)

        if supplier_id:
            query = query.filter(Product.supplier_id == int(supplier_id))

        if in_stock:
            query = query.filter(
                Product.in_stock == (in_stock.lower() == "true")
            )

        # Execute query with pagination
        products = query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        # Format response
        products_data = []
        for product in products.items:
            products_data.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "category": product.category,
                    "price": float(product.price) if product.price else None,
                    "unit": product.unit,
                    "sku": product.sku,
                    "in_stock": product.in_stock,
                    "supplier_id": product.supplier_id,
                    "supplier_name": (
                        product.supplier.name if product.supplier else None
                    ),
                    "created_at": (
                        product.created_at.isoformat()
                        if product.created_at
                        else None
                    ),
                    "updated_at": (
                        product.updated_at.isoformat()
                        if product.updated_at
                        else None
                    ),
                }
            )

        return jsonify(
            {
                "products": products_data,
                "pagination": {
                    "page": products.page,
                    "pages": products.pages,
                    "per_page": products.per_page,
                    "total": products.total,
                    "has_next": products.has_next,
                    "has_prev": products.has_prev,
                },
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@products_bp.route("/api/products", methods=["POST"])
def create_product():
    """Create a new product"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get("name"):
            return jsonify({"error": "Product name is required"}), 400

        # Create new product
        product = Product(
            name=data["name"],
            description=data.get("description"),
            category=data.get("category"),
            price=float(data["price"]) if data.get("price") else None,
            unit=data.get("unit"),
            sku=data.get("sku"),
            in_stock=data.get("in_stock", True),
            supplier_id=(
                int(data["supplier_id"]) if data.get("supplier_id") else None
            ),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.session.add(product)
        db.session.commit()

        return (
            jsonify(
                {
                    "id": product.id,
                    "name": product.name,
                    "message": "Product created successfully",
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@products_bp.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    """Update an existing product"""
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()

        # Update fields
        if "name" in data:
            product.name = data["name"]
        if "description" in data:
            product.description = data["description"]
        if "category" in data:
            product.category = data["category"]
        if "price" in data:
            product.price = float(data["price"]) if data["price"] else None
        if "unit" in data:
            product.unit = data["unit"]
        if "sku" in data:
            product.sku = data["sku"]
        if "in_stock" in data:
            product.in_stock = data["in_stock"]
        if "supplier_id" in data:
            product.supplier_id = (
                int(data["supplier_id"]) if data["supplier_id"] else None
            )

        product.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify(
            {
                "id": product.id,
                "name": product.name,
                "message": "Product updated successfully",
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@products_bp.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """Delete a product"""
    try:
        product = Product.query.get_or_404(product_id)

        db.session.delete(product)
        db.session.commit()

        return jsonify({"message": "Product deleted successfully"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@products_bp.route("/api/products/categories", methods=["GET"])
def get_product_categories():
    """Get all unique product categories"""
    try:
        categories = (
            db.session.query(Product.category)
            .filter(Product.category.isnot(None), Product.category != "")
            .distinct()
            .all()
        )

        categories_list = [cat[0] for cat in categories]

        return jsonify({"categories": sorted(categories_list)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@products_bp.route("/api/products/stats", methods=["GET"])
def get_product_stats():
    """Get product statistics for dashboard"""
    try:
        total_products = Product.query.count()
        in_stock_products = Product.query.filter_by(in_stock=True).count()
        out_of_stock_products = Product.query.filter_by(in_stock=False).count()

        # Category distribution
        category_stats = (
            db.session.query(Product.category, db.func.count(Product.id))
            .filter(Product.category.isnot(None))
            .group_by(Product.category)
            .all()
        )

        category_distribution = {cat: count for cat, count in category_stats}

        # Price statistics
        price_stats = (
            db.session.query(
                db.func.min(Product.price),
                db.func.max(Product.price),
                db.func.avg(Product.price),
            )
            .filter(Product.price.isnot(None))
            .first()
        )

        return jsonify(
            {
                "total_products": total_products,
                "in_stock_products": in_stock_products,
                "out_of_stock_products": out_of_stock_products,
                "category_distribution": category_distribution,
                "price_stats": {
                    "min_price": (
                        float(price_stats[0]) if price_stats[0] else 0
                    ),
                    "max_price": (
                        float(price_stats[1]) if price_stats[1] else 0
                    ),
                    "avg_price": (
                        float(price_stats[2]) if price_stats[2] else 0
                    ),
                },
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@products_bp.route("/api/products/import", methods=["POST"])
def import_products():
    """Import products from Excel/CSV file"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        # Read file based on extension
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.StringIO(file.read().decode("utf-8")))
        elif file.filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(file.read()))
        else:
            return (
                jsonify(
                    {
                        "error": "Unsupported file format. Use CSV or Excel files."
                    }
                ),
                400,
            )

        imported_count = 0
        errors = []

        # Expected columns mapping
        column_mapping = {
            "name": ["name", "product_name", "product", "naam"],
            "description": ["description", "desc", "omschrijving"],
            "category": ["category", "cat", "categorie"],
            "price": ["price", "prijs", "cost", "kosten"],
            "unit": ["unit", "eenheid", "measure"],
            "sku": ["sku", "code", "product_code"],
            "supplier": ["supplier", "leverancier", "vendor"],
        }

        # Normalize column names
        df.columns = df.columns.str.lower().str.strip()

        for index, row in df.iterrows():
            try:
                # Map columns
                product_data = {}
                for field, possible_names in column_mapping.items():
                    for col_name in possible_names:
                        if col_name in df.columns:
                            product_data[field] = row[col_name]
                            break

                # Skip if no name
                if not product_data.get("name") or pd.isna(
                    product_data["name"]
                ):
                    errors.append(f"Row {index + 1}: Missing product name")
                    continue

                # Find or create supplier
                supplier_id = None
                if product_data.get("supplier") and not pd.isna(
                    product_data["supplier"]
                ):
                    supplier = Supplier.query.filter_by(
                        name=str(product_data["supplier"])
                    ).first()
                    if supplier:
                        supplier_id = supplier.id

                # Create product
                product = Product(
                    name=str(product_data["name"]),
                    description=(
                        str(product_data.get("description", ""))
                        if product_data.get("description")
                        and not pd.isna(product_data.get("description"))
                        else None
                    ),
                    category=(
                        str(product_data.get("category", ""))
                        if product_data.get("category")
                        and not pd.isna(product_data.get("category"))
                        else None
                    ),
                    price=(
                        float(product_data["price"])
                        if product_data.get("price")
                        and not pd.isna(product_data["price"])
                        else None
                    ),
                    unit=(
                        str(product_data.get("unit", ""))
                        if product_data.get("unit")
                        and not pd.isna(product_data.get("unit"))
                        else None
                    ),
                    sku=(
                        str(product_data.get("sku", ""))
                        if product_data.get("sku")
                        and not pd.isna(product_data.get("sku"))
                        else None
                    ),
                    supplier_id=supplier_id,
                    in_stock=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )

                db.session.add(product)
                imported_count += 1

            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")

        db.session.commit()

        return jsonify(
            {
                "imported_count": imported_count,
                "errors": errors,
                "message": f"Successfully imported {imported_count} products",
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@products_bp.route("/api/products/export", methods=["GET"])
def export_products():
    """Export all products to JSON"""
    try:
        products = Product.query.join(
            Supplier, Product.supplier_id == Supplier.id, isouter=True
        ).all()

        products_data = []
        for product in products:
            products_data.append(
                {
                    "name": product.name,
                    "description": product.description,
                    "category": product.category,
                    "price": float(product.price) if product.price else None,
                    "unit": product.unit,
                    "sku": product.sku,
                    "in_stock": product.in_stock,
                    "supplier_name": (
                        product.supplier.name if product.supplier else None
                    ),
                    "created_at": (
                        product.created_at.isoformat()
                        if product.created_at
                        else None
                    ),
                }
            )

        return jsonify(
            {
                "products": products_data,
                "count": len(products_data),
                "exported_at": datetime.utcnow().isoformat(),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
