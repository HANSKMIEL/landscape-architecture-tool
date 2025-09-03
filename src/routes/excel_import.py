# Excel Import System API Routes
# File location: src/routes/excel_import.py
# This file handles Excel file import operations for bulk data management

import io
import logging
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
from flask import Blueprint, jsonify, request, send_file
from werkzeug.utils import secure_filename

from src.models.landscape import (
    Client,
    Plant,
    Product,
    Supplier,
    db,
)
from src.schemas import (
    ClientCreateSchema,
    PlantCreateSchema,
    ProductCreateSchema,
    SupplierCreateSchema,
)

excel_import_bp = Blueprint("excel_import", __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {"xlsx", "xls", "csv"}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@excel_import_bp.route("/import/validate-file", methods=["POST"])
def validate_import_file():
    """Validate uploaded Excel/CSV file structure"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "Geen bestand geselecteerd"}), 400

        file = request.files["file"]
        import_type = request.form.get("type", "suppliers")  # suppliers, plants, products, clients

        if file.filename == "":
            return jsonify({"error": "Geen bestand geselecteerd"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Ongeldig bestandsformaat. Gebruik .xlsx, .xls of .csv"}), 400

        # Read file into pandas DataFrame
        file_content = file.read()
        file.seek(0)  # Reset file pointer

        try:
            if file.filename.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(file_content))
            else:
                df = pd.read_excel(io.BytesIO(file_content))
        except Exception as e:
            return jsonify({"error": f"Fout bij lezen bestand: {e!s}"}), 400

        # Validate file structure based on import type
        validation_result = validate_file_structure(df, import_type)

        return jsonify(validation_result)

    except Exception as e:
        logging.exception("Error validating import file")
        return jsonify({"error": f"Fout bij valideren bestand: {e!s}"}), 500


def validate_file_structure(df: pd.DataFrame, import_type: str) -> dict[str, Any]:
    """Validate DataFrame structure for import type"""

    required_columns = {
        "suppliers": [
            "name",
            "contact_person",
            "email",
            "phone",
            "address",
            "city",
            "postal_code",
            "website",
            "specialization",
            "notes",
        ],
        "plants": [
            "name",
            "common_name",
            "category",
            "sun_requirements",
            "water_needs",
            "hardiness_zone",
            "height_max",
            "width_max",
            "bloom_time",
            "bloom_color",
            "maintenance",
            "supplier_id",
        ],
        "products": ["name", "category", "description", "price", "unit", "supplier_id"],
        "clients": ["name", "email", "phone", "address", "city", "postal_code", "country", "client_type"],
    }

    optional_columns = {
        "suppliers": ["website", "specialization", "notes"],
        "plants": ["notes", "native_region", "soil_type"],
        "products": ["stock_quantity", "notes"],
        "clients": ["company", "notes"],
    }

    if import_type not in required_columns:
        return {
            "valid": False,
            "error": f"Ongeldig import type: {import_type}",
            "required_columns": [],
            "missing_columns": [],
            "extra_columns": [],
            "sample_data": [],
        }

    required_cols = required_columns[import_type]
    optional_cols = optional_columns.get(import_type, [])
    all_expected_cols = required_cols + optional_cols

    # Check for missing required columns
    missing_columns = [col for col in required_cols if col not in df.columns]

    # Check for extra columns (not required or optional)
    extra_columns = [col for col in df.columns if col not in all_expected_cols]

    # Get sample data (first 3 rows)
    sample_data = []
    if len(df) > 0:
        sample_rows = df.head(3).fillna("")
        sample_data = sample_rows.to_dict("records")

    # Check data quality
    data_issues = []
    if len(df) == 0:
        data_issues.append("Bestand bevat geen data rijen")

    # Validate specific columns based on import type
    if import_type == "suppliers" and len(df) > 0:
        if "email" in df.columns:
            invalid_emails = df[df["email"].notna() & ~df["email"].str.contains("@", na=False)]
            if len(invalid_emails) > 0:
                data_issues.append(f"{len(invalid_emails)} ongeldige email adressen gevonden")

    if import_type == "plants" and len(df) > 0:
        if "supplier_id" in df.columns:
            invalid_supplier_ids = df[
                df["supplier_id"].notna() & ~df["supplier_id"].astype(str).str.match(r"^\d+$", na=False)
            ]
            if len(invalid_supplier_ids) > 0:
                data_issues.append(f"{len(invalid_supplier_ids)} ongeldige leverancier IDs gevonden")

    if import_type == "products" and len(df) > 0:
        if "price" in df.columns:
            invalid_prices = df[df["price"].notna() & ~pd.to_numeric(df["price"], errors="coerce").notna()]
            if len(invalid_prices) > 0:
                data_issues.append(f"{len(invalid_prices)} ongeldige prijzen gevonden")

    is_valid = len(missing_columns) == 0 and len(data_issues) == 0

    return {
        "valid": is_valid,
        "total_rows": len(df),
        "required_columns": required_cols,
        "optional_columns": optional_cols,
        "missing_columns": missing_columns,
        "extra_columns": extra_columns,
        "data_issues": data_issues,
        "sample_data": sample_data,
        "recommendations": get_import_recommendations(import_type, df, missing_columns, extra_columns),
    }


def get_import_recommendations(
    import_type: str, df: pd.DataFrame, missing_columns: list[str], extra_columns: list[str]
) -> list[str]:
    """Get recommendations for improving the import file"""
    recommendations = []

    if missing_columns:
        recommendations.append(f"Voeg de volgende kolommen toe: {', '.join(missing_columns)}")

    if extra_columns:
        recommendations.append(f"Optioneel: verwijder onnodige kolommen: {', '.join(extra_columns)}")

    if import_type == "plants" and "supplier_id" in df.columns:
        # Check if supplier IDs exist
        unique_supplier_ids = df["supplier_id"].dropna().unique()
        existing_suppliers = db.session.query(Supplier.id).filter(Supplier.id.in_(unique_supplier_ids)).all()
        existing_ids = [sid[0] for sid in existing_suppliers]
        missing_supplier_ids = [sid for sid in unique_supplier_ids if int(sid) not in existing_ids]

        if missing_supplier_ids:
            recommendations.append(
                f"Leverancier IDs niet gevonden: {', '.join(map(str, missing_supplier_ids))}. Importeer eerst leveranciers."
            )

    if import_type == "products" and "supplier_id" in df.columns:
        # Check if supplier IDs exist
        unique_supplier_ids = df["supplier_id"].dropna().unique()
        existing_suppliers = db.session.query(Supplier.id).filter(Supplier.id.in_(unique_supplier_ids)).all()
        existing_ids = [sid[0] for sid in existing_suppliers]
        missing_supplier_ids = [sid for sid in unique_supplier_ids if int(sid) not in existing_ids]

        if missing_supplier_ids:
            recommendations.append(
                f"Leverancier IDs niet gevonden: {', '.join(map(str, missing_supplier_ids))}. Importeer eerst leveranciers."
            )

    if len(df) > 1000:
        recommendations.append(
            "Groot bestand gedetecteerd. Overweeg het opsplitsen in kleinere bestanden voor betere prestaties."
        )

    return recommendations


@excel_import_bp.route("/api/import/process", methods=["POST"])
def process_import():
    """Process validated Excel/CSV file and import data"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "Geen bestand geselecteerd"}), 400

        file = request.files["file"]
        import_type = request.form.get("type", "suppliers")
        update_existing = request.form.get("update_existing", "false").lower() == "true"

        if not allowed_file(file.filename):
            return jsonify({"error": "Ongeldig bestandsformaat"}), 400

        # Read file into pandas DataFrame
        file_content = file.read()

        try:
            if file.filename.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(file_content))
            else:
                df = pd.read_excel(io.BytesIO(file_content))
        except Exception as e:
            return jsonify({"error": f"Fout bij lezen bestand: {e!s}"}), 400

        # Validate again before processing
        validation_result = validate_file_structure(df, import_type)
        if not validation_result["valid"]:
            return jsonify({"error": "Bestand validatie gefaald", "validation_result": validation_result}), 400

        # Process the import
        import_result = process_import_data(df, import_type, update_existing)

        return jsonify(import_result)

    except Exception as e:
        logging.exception("Error processing import")
        return jsonify({"error": f"Fout bij verwerken import: {e!s}"}), 500


def process_import_data(df: pd.DataFrame, import_type: str, update_existing: bool) -> dict[str, Any]:
    """Process DataFrame and import data into database"""

    successful_imports = 0
    failed_imports = 0
    updated_records = 0
    errors = []

    try:
        for index, row in df.iterrows():
            try:
                row_dict = row.fillna("").to_dict()

                if import_type == "suppliers":
                    result = import_supplier_row(row_dict, update_existing)
                elif import_type == "plants":
                    result = import_plant_row(row_dict, update_existing)
                elif import_type == "products":
                    result = import_product_row(row_dict, update_existing)
                elif import_type == "clients":
                    result = import_client_row(row_dict, update_existing)
                else:
                    raise ValueError(f"Ongeldig import type: {import_type}")

                if result["success"]:
                    if result.get("updated"):
                        updated_records += 1
                    else:
                        successful_imports += 1
                else:
                    failed_imports += 1
                    errors.append(f"Rij {index + 2}: {result['error']}")

            except Exception as e:
                failed_imports += 1
                errors.append(f"Rij {index + 2}: {e!s}")

        # Commit all changes
        db.session.commit()

        return {
            "success": True,
            "total_rows": len(df),
            "successful_imports": successful_imports,
            "updated_records": updated_records,
            "failed_imports": failed_imports,
            "errors": errors[:10],  # Limit to first 10 errors
            "message": f"Import voltooid: {successful_imports} nieuwe records, {updated_records} bijgewerkt, {failed_imports} gefaald",
        }

    except Exception as e:
        db.session.rollback()
        raise e


def import_supplier_row(row_dict: dict[str, Any], update_existing: bool) -> dict[str, Any]:
    """Import single supplier row"""
    try:
        # Check if supplier already exists
        existing_supplier = Supplier.query.filter_by(name=row_dict["name"], email=row_dict["email"]).first()

        if existing_supplier and not update_existing:
            return {"success": False, "error": "Leverancier bestaat al"}

        supplier_data = {
            "name": row_dict["name"],
            "contact_person": row_dict["contact_person"],
            "email": row_dict["email"],
            "phone": row_dict["phone"],
            "address": row_dict["address"],
            "city": row_dict["city"],
            "postal_code": row_dict["postal_code"],
            "website": row_dict.get("website", ""),
            "specialization": row_dict.get("specialization", ""),
            "notes": row_dict.get("notes", ""),
        }

        if existing_supplier and update_existing:
            # Update existing supplier
            for key, value in supplier_data.items():
                setattr(existing_supplier, key, value)
            return {"success": True, "updated": True}
        # Create new supplier
        supplier = Supplier(**supplier_data)
        db.session.add(supplier)
        return {"success": True, "updated": False}

    except Exception as e:
        return {"success": False, "error": str(e)}


def import_plant_row(row_dict: dict[str, Any], update_existing: bool) -> dict[str, Any]:
    """Import single plant row"""
    try:
        # Check if plant already exists
        existing_plant = Plant.query.filter_by(name=row_dict["name"]).first()

        if existing_plant and not update_existing:
            return {"success": False, "error": "Plant bestaat al"}

        # Validate supplier_id
        supplier_id = row_dict.get("supplier_id")
        if supplier_id:
            supplier = db.session.get(Supplier, int(supplier_id))
            if not supplier:
                return {"success": False, "error": f"Leverancier ID {supplier_id} niet gevonden"}
        else:
            supplier_id = None

        plant_data = {
            "name": row_dict["name"],
            "common_name": row_dict["common_name"],
            "category": row_dict["category"],
            "sun_requirements": row_dict["sun_requirements"],
            "water_needs": row_dict["water_needs"],
            "hardiness_zone": row_dict["hardiness_zone"],
            "height_max": float(row_dict["height_max"]) if row_dict.get("height_max") else None,
            "width_max": float(row_dict["width_max"]) if row_dict.get("width_max") else None,
            "bloom_time": row_dict["bloom_time"],
            "bloom_color": row_dict["bloom_color"],
            "maintenance": row_dict["maintenance"],
            "supplier_id": supplier_id,
            "notes": row_dict.get("notes", ""),
            "native_region": row_dict.get("native_region", ""),
            "soil_type": row_dict.get("soil_type", ""),
        }

        if existing_plant and update_existing:
            # Update existing plant
            for key, value in plant_data.items():
                setattr(existing_plant, key, value)
            return {"success": True, "updated": True}
        # Create new plant
        plant = Plant(**plant_data)
        db.session.add(plant)
        return {"success": True, "updated": False}

    except Exception as e:
        return {"success": False, "error": str(e)}


def import_product_row(row_dict: dict[str, Any], update_existing: bool) -> dict[str, Any]:
    """Import single product row"""
    try:
        # Check if product already exists
        existing_product = Product.query.filter_by(
            name=row_dict["name"], supplier_id=int(row_dict["supplier_id"]) if row_dict.get("supplier_id") else None
        ).first()

        if existing_product and not update_existing:
            return {"success": False, "error": "Product bestaat al"}

        # Validate supplier_id
        supplier_id = row_dict.get("supplier_id")
        if supplier_id:
            supplier = db.session.get(Supplier, int(supplier_id))
            if not supplier:
                return {"success": False, "error": f"Leverancier ID {supplier_id} niet gevonden"}
        else:
            supplier_id = None

        product_data = {
            "name": row_dict["name"],
            "category": row_dict["category"],
            "description": row_dict["description"],
            "price": float(row_dict["price"]) if row_dict.get("price") else None,
            "unit": row_dict["unit"],
            "supplier_id": supplier_id,
            "stock_quantity": int(row_dict["stock_quantity"]) if row_dict.get("stock_quantity") else None,
            "notes": row_dict.get("notes", ""),
        }

        if existing_product and update_existing:
            # Update existing product
            for key, value in product_data.items():
                setattr(existing_product, key, value)
            return {"success": True, "updated": True}
        # Create new product
        product = Product(**product_data)
        db.session.add(product)
        return {"success": True, "updated": False}

    except Exception as e:
        return {"success": False, "error": str(e)}


def import_client_row(row_dict: dict[str, Any], update_existing: bool) -> dict[str, Any]:
    """Import single client row"""
    try:
        # Check if client already exists
        existing_client = Client.query.filter_by(email=row_dict["email"]).first()

        if existing_client and not update_existing:
            return {"success": False, "error": "Klant bestaat al"}

        client_data = {
            "name": row_dict["name"],
            "email": row_dict["email"],
            "phone": row_dict["phone"],
            "address": row_dict["address"],
            "city": row_dict["city"],
            "postal_code": row_dict["postal_code"],
            "country": row_dict["country"],
            "client_type": row_dict["client_type"],
            "company": row_dict.get("company", ""),
            "notes": row_dict.get("notes", ""),
        }

        if existing_client and update_existing:
            # Update existing client
            for key, value in client_data.items():
                setattr(existing_client, key, value)
            return {"success": True, "updated": True}
        # Create new client
        client = Client(**client_data)
        db.session.add(client)
        return {"success": True, "updated": False}

    except Exception as e:
        return {"success": False, "error": str(e)}


@excel_import_bp.route("/api/import/template/<import_type>", methods=["GET"])
def download_template(import_type):
    """Download Excel template for specific import type"""
    try:
        templates = {
            "suppliers": {
                "columns": [
                    "name",
                    "contact_person",
                    "email",
                    "phone",
                    "address",
                    "city",
                    "postal_code",
                    "website",
                    "specialization",
                    "notes",
                ],
                "sample_data": [
                    [
                        "Boomkwekerij Peters",
                        "Jan Peters",
                        "info@boomkwekerij-peters.nl",
                        "+31 20 1234567",
                        "Kwekerslaan 1",
                        "Amsterdam",
                        "1000 AB",
                        "www.boomkwekerij-peters.nl",
                        "Bomen en heesters",
                        "Gespecialiseerd in grote bomen",
                    ],
                    [
                        "Tuincentrum De Groene Vingers",
                        "Marie de Vries",
                        "verkoop@groenvingers.nl",
                        "+31 30 9876543",
                        "Tuinstraat 15",
                        "Utrecht",
                        "3500 CD",
                        "www.groenvingers.nl",
                        "Tuinplanten",
                        "Breed assortiment tuinplanten",
                    ],
                ],
            },
            "plants": {
                "columns": [
                    "name",
                    "common_name",
                    "category",
                    "sun_requirements",
                    "water_needs",
                    "hardiness_zone",
                    "height_max",
                    "width_max",
                    "bloom_time",
                    "bloom_color",
                    "maintenance",
                    "supplier_id",
                    "notes",
                    "native_region",
                    "soil_type",
                ],
                "sample_data": [
                    [
                        "Acer palmatum",
                        "Japanse esdoorn",
                        "Boom",
                        "Halfschaduw",
                        "Gemiddeld",
                        "6",
                        "8.0",
                        "6.0",
                        "April-Mei",
                        "Rood",
                        "Gemiddeld",
                        "1",
                        "Prachtige herfstkleur",
                        "Japan",
                        "Humusrijk",
                    ],
                    [
                        "Lavandula angustifolia",
                        "Lavendel",
                        "Vaste plant",
                        "Zon",
                        "Weinig",
                        "5",
                        "0.6",
                        "0.8",
                        "Juli-September",
                        "Paars",
                        "Laag",
                        "2",
                        "Geurig en bijenvriendelijk",
                        "Middellandse Zee",
                        "Doorlatend",
                    ],
                ],
            },
            "products": {
                "columns": [
                    "name",
                    "category",
                    "description",
                    "price",
                    "unit",
                    "supplier_id",
                    "stock_quantity",
                    "notes",
                ],
                "sample_data": [
                    [
                        "Potgrond universeel 40L",
                        "Grond en voeding",
                        "Hoogwaardige potgrond voor alle planten",
                        "8.95",
                        "zak",
                        "1",
                        "50",
                        "Geschikt voor binnen en buiten",
                    ],
                    [
                        "Tuinslang 25m",
                        "Gereedschap",
                        "Flexibele tuinslang met spuitpistool",
                        "45.00",
                        "stuk",
                        "2",
                        "15",
                        "Inclusief koppelingen",
                    ],
                ],
            },
            "clients": {
                "columns": [
                    "name",
                    "email",
                    "phone",
                    "address",
                    "city",
                    "postal_code",
                    "country",
                    "client_type",
                    "company",
                    "notes",
                ],
                "sample_data": [
                    [
                        "Gemeente Amsterdam",
                        "projecten@amsterdam.nl",
                        "+31 20 5551234",
                        "Stopera 1",
                        "Amsterdam",
                        "1012 AB",
                        "Nederland",
                        "Zakelijk",
                        "Gemeente Amsterdam",
                        "Grote openbare projecten",
                    ],
                    [
                        "Familie Jansen",
                        "j.jansen@email.nl",
                        "+31 6 12345678",
                        "Dorpsstraat 25",
                        "Hilversum",
                        "1234 AB",
                        "Nederland",
                        "Particulier",
                        "",
                        "Privé tuin renovatie",
                    ],
                ],
            },
        }

        if import_type not in templates:
            return jsonify({"error": f"Ongeldig template type: {import_type}"}), 400

        template_data = templates[import_type]

        # Create Excel file
        df = pd.DataFrame([template_data["columns"]] + template_data["sample_data"])
        df.columns = range(len(df.columns))  # Reset column names to avoid header issues

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=f"{import_type}_template", index=False, header=False)

            # Style the header row
            worksheet = writer.sheets[f"{import_type}_template"]

            # Bold header row
            for col in range(len(template_data["columns"])):
                cell = worksheet.cell(row=1, column=col + 1)
                cell.font = cell.font.copy(bold=True)

        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name=f"{import_type}_import_template.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    except Exception as e:
        logging.exception("Error generating template")
        return jsonify({"error": f"Fout bij genereren template: {e!s}"}), 500


@excel_import_bp.route("/api/import/status", methods=["GET"])
def get_import_status():
    """Get current import statistics"""
    try:
        stats = {
            "suppliers": Supplier.query.count(),
            "plants": Plant.query.count(),
            "products": Product.query.count(),
            "clients": Client.query.count(),
        }

        return jsonify(
            {
                "current_counts": stats,
                "supported_formats": list(ALLOWED_EXTENSIONS),
                "max_file_size": "10MB",
                "import_types": ["suppliers", "plants", "products", "clients"],
            }
        )

    except Exception as e:
        logging.exception("Error getting import status")
        return jsonify({"error": f"Fout bij ophalen import status: {e!s}"}), 500
