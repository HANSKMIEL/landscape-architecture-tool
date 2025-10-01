# Reports API Routes
# File location: src/routes/reports.py
# This file handles all report generation operations

import io
import logging
from datetime import UTC, datetime

from flask import Blueprint, jsonify, request, send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from src.models.landscape import (
    Client,
    Plant,
    Product,
    Project,
    ProjectPlant,
    Supplier,
    db,
)
from src.routes.user import login_required

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/api/reports/business-summary", methods=["GET"])
@login_required
def generate_business_summary():
    """Generate business summary report"""
    try:
        # Get date range parameters
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        format_type = request.args.get("format", "json")  # json or pdf

        # Build date filter
        date_filter = []
        if start_date:
            date_filter.append(Project.created_at >= datetime.fromisoformat(start_date))
        if end_date:
            date_filter.append(Project.created_at <= datetime.fromisoformat(end_date))

        # Get statistics
        total_projects = Project.query.filter(*date_filter).count()
        total_clients = Client.query.count()
        total_plants = Plant.query.count()
        total_products = Product.query.count()
        total_suppliers = Supplier.query.count()

        # Project status distribution
        status_stats = (
            db.session.query(Project.status, db.func.count(Project.id))
            .filter(*date_filter)
            .group_by(Project.status)
            .all()
        )

        status_distribution = dict(status_stats)

        # Budget statistics
        budget_stats = (
            db.session.query(
                db.func.sum(Project.budget),
                db.func.avg(Project.budget),
            )
            .filter(Project.budget.isnot(None), *date_filter)
            .first()
        )

        total_budget = float(budget_stats[0]) if budget_stats[0] else 0
        total_spent = 0  # No spent field in current model
        avg_budget = float(budget_stats[1]) if budget_stats[1] else 0

        # Top clients by project count
        top_clients = (
            db.session.query(
                Client.name,
                Client.client_type,
                db.func.count(Project.id).label("project_count"),
                db.func.sum(Project.budget).label("total_budget"),
            )
            .join(Project)
            .filter(*date_filter)
            .group_by(Client.id, Client.name, Client.client_type)
            .order_by(db.desc("project_count"))
            .limit(10)
            .all()
        )

        top_clients_data = []
        for name, client_type, count, budget in top_clients:
            top_clients_data.append(
                {
                    "name": name,
                    "client_type": client_type,
                    "project_count": count,
                    "total_budget": float(budget) if budget else 0,
                }
            )

        # Most used plants
        plant_usage = (
            db.session.query(
                Plant.name,
                Plant.common_name,
                db.func.count(ProjectPlant.project_id.distinct()).label("project_count"),
            )
            .join(ProjectPlant, Plant.id == ProjectPlant.plant_id)
            .join(Project, ProjectPlant.project_id == Project.id)
            .filter(*date_filter)
            .group_by(Plant.id, Plant.name, Plant.common_name)
            .order_by(db.func.count(ProjectPlant.project_id.distinct()).desc())
            .limit(10)
            .all()
        )

        plant_usage_data = []
        for name, common_name, count in plant_usage:
            plant_usage_data.append(
                {
                    "name": name,
                    "common_name": common_name,
                    "project_count": count,
                }
            )

        # Most used products - disabled for now as Product-Project
        # relationship not directly modeled
        product_usage_data = []

        report_data = {
            "generated_at": datetime.now(UTC).isoformat(),
            "period": {"start_date": start_date, "end_date": end_date},
            "summary": {
                "total_projects": total_projects,
                "total_clients": total_clients,
                "total_plants": total_plants,
                "total_products": total_products,
                "total_suppliers": total_suppliers,
            },
            "project_stats": {
                "status_distribution": status_distribution,
                "budget_stats": {
                    "total_budget": total_budget,
                    "total_spent": total_spent,
                    "avg_budget": avg_budget,
                    "utilization_rate": ((total_spent / total_budget * 100) if total_budget > 0 else 0),
                },
            },
            "top_clients": top_clients_data,
            "plant_usage": plant_usage_data,
            "product_usage": product_usage_data,
        }

        if format_type == "pdf":
            return generate_business_summary_pdf(report_data)

        return jsonify(report_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def generate_business_summary_pdf(data):
    """Generate PDF version of business summary report"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor("#2D5016"),
        )
        story.append(Paragraph("Landscape Architecture Business Summary", title_style))
        story.append(Spacer(1, 20))

        # Generation info
        story.append(
            Paragraph(
                (f"Generated: " f"{datetime.now(UTC).strftime('%B %d, %Y at %H:%M')}"),
                styles["Normal"],
            )
        )
        if data["period"]["start_date"] and data["period"]["end_date"]:
            story.append(
                Paragraph(
                    f"Period: {data['period']['start_date']} " f"to {data['period']['end_date']}",
                    styles["Normal"],
                )
            )
        story.append(Spacer(1, 20))

        # Summary statistics
        story.append(Paragraph("Business Overview", styles["Heading2"]))
        summary_data = [
            ["Metric", "Count"],
            ["Total Projects", str(data["summary"]["total_projects"])],
            ["Total Clients", str(data["summary"]["total_clients"])],
            ["Total Plants", str(data["summary"]["total_plants"])],
            ["Total Products", str(data["summary"]["total_products"])],
            ["Total Suppliers", str(data["summary"]["total_suppliers"])],
        ]

        summary_table = Table(summary_data, colWidths=[3 * inch, 1.5 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#2D5016"),
                    ),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(summary_table)
        story.append(Spacer(1, 20))

        # Project status distribution
        if data["project_stats"]["status_distribution"]:
            story.append(Paragraph("Project Status Distribution", styles["Heading2"]))
            status_data = [["Status", "Count"]]
            for status, count in data["project_stats"]["status_distribution"].items():
                status_data.append([status.replace("_", " ").title(), str(count)])

            status_table = Table(status_data, colWidths=[3 * inch, 1.5 * inch])
            status_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.HexColor("#2D5016"),
                        ),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 12),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            story.append(status_table)
            story.append(Spacer(1, 20))

        # Budget statistics
        budget_stats = data["project_stats"]["budget_stats"]
        if budget_stats["total_budget"] > 0:
            story.append(Paragraph("Financial Overview", styles["Heading2"]))
            budget_data = [
                ["Metric", "Amount (€)"],
                ["Total Budget", f"€{budget_stats['total_budget']:,.2f}"],
                ["Total Spent", f"€{budget_stats['total_spent']:,.2f}"],
                ["Average Budget", f"€{budget_stats['avg_budget']:,.2f}"],
                [
                    "Utilization Rate",
                    f"{budget_stats['utilization_rate']:.1f}%",
                ],
            ]

            budget_table = Table(budget_data, colWidths=[3 * inch, 1.5 * inch])
            budget_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.HexColor("#2D5016"),
                        ),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 12),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            story.append(budget_table)
            story.append(Spacer(1, 20))

        # Top clients
        if data["top_clients"]:
            story.append(Paragraph("Top Clients by Project Count", styles["Heading2"]))
            client_data = [["Client", "Type", "Projects", "Total Budget (€)"]]
            for client in data["top_clients"][:5]:  # Top 5
                client_data.append(
                    [
                        client["name"],
                        client["client_type"] or "-",
                        str(client["project_count"]),
                        (f"€{client['total_budget']:,.2f}" if client["total_budget"] else "€0.00"),
                    ]
                )

            client_table = Table(
                client_data,
                colWidths=[1.5 * inch, 1.5 * inch, 1 * inch, 1.5 * inch],
            )
            client_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.HexColor("#2D5016"),
                        ),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            story.append(client_table)
            story.append(Spacer(1, 20))

        # Most used plants
        if data["plant_usage"]:
            story.append(Paragraph("Most Used Plants", styles["Heading2"]))
            plant_data = [["Plant Name", "Common Name", "Projects"]]
            for plant in data["plant_usage"][:5]:  # Top 5
                plant_data.append(
                    [
                        plant["name"],
                        plant["common_name"] or "-",
                        str(plant["project_count"]),
                    ]
                )

            plant_table = Table(plant_data, colWidths=[2 * inch, 2 * inch, 1 * inch])
            plant_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.HexColor("#2D5016"),
                        ),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            story.append(plant_table)

        doc.build(story)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=(f'business_summary_{datetime.now(UTC).strftime("%Y%m%d")}.pdf'),
            mimetype="application/pdf",
        )

    except Exception:
        logging.exception("Error generating business summary PDF")
        return jsonify({"error": "Failed to generate PDF report. Please try again later."}), 500


@reports_bp.route("/api/reports/project/<int:project_id>", methods=["GET"])
def generate_project_report(project_id):
    """Generate detailed project report"""
    try:
        format_type = request.args.get("format", "json")  # json or pdf

        project = db.session.get(Project, project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404

        # Get project plants with details
        plants_data = []
        for project_plant in project.project_plants:
            plant = project_plant.plant
            if plant:
                plants_data.append(
                    {
                        "name": plant.name,
                        "common_name": plant.common_name,
                        "category": plant.category,
                        "sun_requirements": plant.sun_requirements,
                        "water_needs": plant.water_needs,
                        "hardiness_zone": plant.hardiness_zone,
                        "height_max": plant.height_max,
                        "width_max": plant.width_max,
                        "bloom_time": plant.bloom_time,
                        "bloom_color": plant.bloom_color,
                        "maintenance": plant.maintenance,
                        "quantity": project_plant.quantity,
                        "unit_cost": project_plant.unit_cost,
                    }
                )

        # Get project products with details - disabled as no direct
        # Product-Project relationship
        products_data = []
        total_product_cost = 0

        report_data = {
            "generated_at": datetime.now(UTC).isoformat(),
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "budget": float(project.budget) if project.budget else 0,
                "spent": 0,  # No spent field in current model
                "location": project.location,
                "area_size": (float(project.area_size) if project.area_size else 0),
                "start_date": (project.start_date.isoformat() if project.start_date else None),
                "end_date": (project.end_date.isoformat() if project.end_date else None),
                "notes": project.notes,
                "created_at": (project.created_at.isoformat() if project.created_at else None),
            },
            "client": {
                "name": project.client.name if project.client else "Unknown",
                "email": project.client.email if project.client else "",
                "phone": project.client.phone if project.client else "",
                "client_type": project.client.client_type if project.client else "",
                "address": project.client.address if project.client else "",
                "city": project.client.city if project.client else "",
                "postal_code": project.client.postal_code if project.client else "",
            },
            "plants": plants_data,
            "products": products_data,
            "summary": {
                "total_plants": len(plants_data),
                "total_products": len(products_data),
                "total_product_cost": total_product_cost,
                "budget_utilization": 0,  # No spent field available
            },
        }

        if format_type == "pdf":
            return generate_project_report_pdf(report_data)

        return jsonify(report_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def generate_project_report_pdf(data):
    """Generate PDF version of project report"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        project = data["project"]
        client = data["client"]

        # Title
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=20,
            spaceAfter=30,
            textColor=colors.HexColor("#2D5016"),
        )
        story.append(Paragraph(f"Project Report: {project['name']}", title_style))
        story.append(Spacer(1, 20))

        # Project details
        story.append(Paragraph("Project Information", styles["Heading2"]))
        project_data = [
            ["Field", "Value"],
            ["Project Name", project["name"]],
            ["Status", project["status"].replace("_", " ").title()],
            ["Location", project["location"] or "-"],
            [
                "Area Size",
                f"{project['area_size']} m²" if project["area_size"] else "-",
            ],
            [
                "Budget",
                f"€{project['budget']:,.2f}" if project["budget"] else "-",
            ],
            [
                "Spent",
                f"€{project['spent']:,.2f}" if project["spent"] else "-",
            ],
            [
                "Start Date",
                project["start_date"][:10] if project["start_date"] else "-",
            ],
            [
                "End Date",
                project["end_date"][:10] if project["end_date"] else "-",
            ],
        ]

        project_table = Table(project_data, colWidths=[2 * inch, 3 * inch])
        project_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#2D5016"),
                    ),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(project_table)
        story.append(Spacer(1, 20))

        # Client information
        story.append(Paragraph("Client Information", styles["Heading2"]))
        client_data = [
            ["Field", "Value"],
            ["Name", client["name"]],
            ["Type", client["client_type"] or "-"],
            ["Email", client["email"]],
            ["Phone", client["phone"] or "-"],
            ["Address", client["address"] or "-"],
            ["City", client["city"] or "-"],
            ["Postal Code", client["postal_code"] or "-"],
        ]

        client_table = Table(client_data, colWidths=[2 * inch, 3 * inch])
        client_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#2D5016"),
                    ),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(client_table)
        story.append(Spacer(1, 20))

        # Plants list
        if data["plants"]:
            story.append(Paragraph("Plant List", styles["Heading2"]))
            plant_data = [["Plant Name", "Common Name", "Category", "Sun", "Water"]]
            for plant in data["plants"]:
                plant_data.append(
                    [
                        plant["name"],
                        plant["common_name"] or "-",
                        plant["category"] or "-",
                        plant["sun_requirements"] or "-",
                        plant["water_needs"] or "-",
                    ]
                )

            plant_table = Table(
                plant_data,
                colWidths=[
                    1.5 * inch,
                    1.5 * inch,
                    1 * inch,
                    0.8 * inch,
                    0.8 * inch,
                ],
            )
            plant_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.HexColor("#2D5016"),
                        ),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            story.append(plant_table)
            story.append(Spacer(1, 20))

        # Products list
        if data["products"]:
            story.append(Paragraph("Product List", styles["Heading2"]))
            product_data = [["Product Name", "Category", "Price (€)", "Supplier"]]
            for product in data["products"]:
                product_data.append(
                    [
                        product["name"],
                        product["category"] or "-",
                        (f"€{product['price']:,.2f}" if product["price"] else "-"),
                        product["supplier_name"] or "-",
                    ]
                )

            product_table = Table(
                product_data,
                colWidths=[2 * inch, 1.2 * inch, 1 * inch, 1.3 * inch],
            )
            product_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.HexColor("#2D5016"),
                        ),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            story.append(product_table)
            story.append(Spacer(1, 20))

        # Project description and notes
        if project["description"]:
            story.append(Paragraph("Project Description", styles["Heading2"]))
            story.append(Paragraph(project["description"], styles["Normal"]))
            story.append(Spacer(1, 20))

        if project["notes"]:
            story.append(Paragraph("Project Notes", styles["Heading2"]))
            story.append(Paragraph(project["notes"], styles["Normal"]))

        doc.build(story)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=(
                f'project_{project["name"].replace(" ", "_")}_' f'{datetime.now(UTC).strftime("%Y%m%d")}.pdf'
            ),
            mimetype="application/pdf",
        )

    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {e!s}"}), 500


@reports_bp.route("/api/reports/plant-usage", methods=["GET"])
def generate_plant_usage_report():
    """Generate plant usage statistics report"""
    try:
        # Get plant usage statistics
        plant_usage = (
            db.session.query(
                Plant.name,
                Plant.common_name,
                Plant.category,
                db.func.count(db.distinct(ProjectPlant.project_id)).label("project_count"),
            )
            .join(ProjectPlant, Plant.id == ProjectPlant.plant_id)
            .group_by(Plant.id, Plant.name, Plant.common_name, Plant.category)
            .order_by(db.desc("project_count"))
            .all()
        )

        usage_data = []
        for name, common_name, category, count in plant_usage:
            usage_data.append(
                {
                    "name": name,
                    "common_name": common_name,
                    "category": category,
                    "project_count": count,
                }
            )

        # Category distribution
        category_stats = (
            db.session.query(
                Plant.category,
                db.func.count(db.distinct(ProjectPlant.project_id)).label("project_count"),
            )
            .join(ProjectPlant, Plant.id == ProjectPlant.plant_id)
            .filter(Plant.category.isnot(None))
            .group_by(Plant.category)
            .order_by(db.desc("project_count"))
            .all()
        )

        category_distribution = dict(category_stats)

        return jsonify(
            {
                "generated_at": datetime.now(UTC).isoformat(),
                "plant_usage": usage_data,
                "category_distribution": category_distribution,
                "total_unique_plants": len(usage_data),
                "most_popular_plant": usage_data[0] if usage_data else None,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reports_bp.route("/api/reports/supplier-performance", methods=["GET"])
def generate_supplier_performance_report():
    """Generate supplier performance report"""
    try:
        # Get supplier statistics
        supplier_stats = (
            db.session.query(
                Supplier.name,
                Supplier.contact_person,
                Supplier.email,
                db.func.count(db.distinct(Product.id)).label("product_count"),
                db.func.count(db.distinct(Project.id)).label("project_count"),
            )
            .outerjoin(Product, Supplier.id == Product.supplier_id)
            .outerjoin(Plant, Supplier.id == Plant.supplier_id)
            .outerjoin(ProjectPlant, Plant.id == ProjectPlant.plant_id)
            .outerjoin(Project, ProjectPlant.project_id == Project.id)
            .group_by(
                Supplier.id,
                Supplier.name,
                Supplier.contact_person,
                Supplier.email,
            )
            .order_by(db.desc("product_count"))
            .all()
        )

        supplier_data = []
        for (
            name,
            contact,
            email,
            product_count,
            project_count,
        ) in supplier_stats:
            supplier_data.append(
                {
                    "name": name,
                    "contact_person": contact,
                    "email": email,
                    "product_count": product_count,
                    "project_count": project_count or 0,
                }
            )

        return jsonify(
            {
                "generated_at": datetime.now(UTC).isoformat(),
                "suppliers": supplier_data,
                "total_suppliers": len(supplier_data),
                "top_supplier": supplier_data[0] if supplier_data else None,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reports_bp.route("/api/reports/generate-pdf", methods=["POST"])
@login_required
def generate_comprehensive_pdf():
    """Generate comprehensive PDF report based on request data"""
    try:
        data = request.get_json()
        report_type = data.get("type", "overview")
        date_range = data.get("dateRange", {})
<<<<<<< HEAD:archive/packages/v1.00D/backend/routes/reports.py
        filters = data.get("filters", {})
        report_data = data.get("data", {})
        language = data.get("language", "en")
        
=======
        report_data = data.get("data", {})
        language = data.get("language", "en")

>>>>>>> origin/main:packages/v1.00D/backend/routes/reports.py
        # Translations for Dutch reports
        translations = {
            "en": {
                "title": "Landscape Architecture Report",
                "generated_on": "Generated on",
                "date_range": "Date Range",
                "overview": "Business Overview",
                "clients": "Client Analysis",
                "projects": "Project Performance",
                "plants": "Plant Analytics",
                "financial": "Financial Summary",
                "total_projects": "Total Projects",
                "total_clients": "Total Clients",
                "total_plants": "Total Plants",
                "total_budget": "Total Budget",
                "average_budget": "Average Budget",
                "project_status": "Project Status Distribution",
                "top_clients": "Top Clients",
                "plant_categories": "Plant Category Distribution",
                "monthly_revenue": "Monthly Revenue",
<<<<<<< HEAD:archive/packages/v1.00D/backend/routes/reports.py
                "page": "Page"
            },
            "nl": {
                "title": "Landschapsarchitectuur Rapport",
                "generated_on": "Gegenereerd op",
                "date_range": "Datumbereik",
                "overview": "Bedrijfsoverzicht",
                "clients": "Klantanalyse",
                "projects": "Projectprestaties",
                "plants": "Plant Analytics",
                "financial": "Financieel Overzicht",
                "total_projects": "Totaal Projecten",
                "total_clients": "Totaal Klanten",
                "total_plants": "Totaal Planten",
                "total_budget": "Totaal Budget",
                "average_budget": "Gemiddeld Budget",
                "project_status": "Project Status Verdeling",
                "top_clients": "Top Klanten",
                "plant_categories": "Plant Categorie Verdeling",
                "monthly_revenue": "Maandelijkse Omzet",
                "page": "Pagina"
            }
        }
        
        t = translations.get(language, translations["en"])
        
=======
                "page": "Page",
            },
            "nl": {
                "title": "Landschapsarchitectuur Rapport",
                "generated_on": "Gegenereerd op",
                "date_range": "Datumbereik",
                "overview": "Bedrijfsoverzicht",
                "clients": "Klantanalyse",
                "projects": "Projectprestaties",
                "plants": "Plant Analytics",
                "financial": "Financieel Overzicht",
                "total_projects": "Totaal Projecten",
                "total_clients": "Totaal Klanten",
                "total_plants": "Totaal Planten",
                "total_budget": "Totaal Budget",
                "average_budget": "Gemiddeld Budget",
                "project_status": "Project Status Verdeling",
                "top_clients": "Top Klanten",
                "plant_categories": "Plant Categorie Verdeling",
                "monthly_revenue": "Maandelijkse Omzet",
                "page": "Pagina",
            },
        }

        t = translations.get(language, translations["en"])

>>>>>>> origin/main:packages/v1.00D/backend/routes/reports.py
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor("#10b981"),
<<<<<<< HEAD:archive/packages/v1.00D/backend/routes/reports.py
            alignment=1  # Center alignment
        )
        
        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor("#374151")
        )
        
=======
            alignment=1,  # Center alignment
        )

>>>>>>> origin/main:packages/v1.00D/backend/routes/reports.py
        # Build PDF content
        story = []

        # Title
        report_titles = {
            "overview": t["overview"],
            "clients": t["clients"],
            "projects": t["projects"],
            "plants": t["plants"],
<<<<<<< HEAD:archive/packages/v1.00D/backend/routes/reports.py
            "financial": t["financial"]
=======
            "financial": t["financial"],
>>>>>>> origin/main:packages/v1.00D/backend/routes/reports.py
        }

        title = f"{t['title']} - {report_titles.get(report_type, t['overview'])}"
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 20))

        # Generation info
        generation_info = f"{t['generated_on']}: {datetime.now().strftime('%d-%m-%Y %H:%M')}"
        if date_range.get("start") and date_range.get("end"):
            generation_info += f"<br/>{t['date_range']}: {date_range['start']} - {date_range['end']}"
<<<<<<< HEAD:archive/packages/v1.00D/backend/routes/reports.py
        
=======

>>>>>>> origin/main:packages/v1.00D/backend/routes/reports.py
        story.append(Paragraph(generation_info, styles["Normal"]))
        story.append(Spacer(1, 30))

        # Report-specific content
        if report_type == "overview":
            story.extend(generate_overview_pdf_content(report_data, t, styles))
        elif report_type == "clients":
            story.extend(generate_clients_pdf_content(report_data, t, styles))
        elif report_type == "projects":
            story.extend(generate_projects_pdf_content(report_data, t, styles))
        elif report_type == "plants":
            story.extend(generate_plants_pdf_content(report_data, t, styles))
        elif report_type == "financial":
            story.extend(generate_financial_pdf_content(report_data, t, styles))

        # Build PDF
        doc.build(story)
        buffer.seek(0)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"landscape_report_{report_type}_{timestamp}.pdf"
<<<<<<< HEAD:archive/packages/v1.00D/backend/routes/reports.py
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf"
        )
        
=======

        return send_file(buffer, as_attachment=True, download_name=filename, mimetype="application/pdf")

>>>>>>> origin/main:packages/v1.00D/backend/routes/reports.py
    except Exception as e:
        logging.error(f"Error generating PDF report: {e!s}")
        return jsonify({"error": str(e)}), 500


def generate_overview_pdf_content(data, t, styles):
    """Generate overview report PDF content"""
    content = []

    # Statistics summary
    if "stats" in data:
        stats = data["stats"]
        content.append(Paragraph("Statistieken Overzicht", styles["Heading2"]))
<<<<<<< HEAD:archive/packages/v1.00D/backend/routes/reports.py
        
=======

>>>>>>> origin/main:packages/v1.00D/backend/routes/reports.py
        stats_data = [
            [t["total_projects"], str(stats.get("projects", 0))],
            [t["total_clients"], str(stats.get("clients", 0))],
            [t["total_plants"], str(stats.get("plants", 0))],
            ["Totaal Producten", str(stats.get("products", 0))],
<<<<<<< HEAD:archive/packages/v1.00D/backend/routes/reports.py
            ["Totaal Leveranciers", str(stats.get("suppliers", 0))]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black)
        ]))
        
=======
            ["Totaal Leveranciers", str(stats.get("suppliers", 0))],
        ]

        stats_table = Table(stats_data, colWidths=[3 * inch, 2 * inch])
        stats_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

>>>>>>> origin/main:packages/v1.00D/backend/routes/reports.py
        content.append(stats_table)
        content.append(Spacer(1, 20))

    # Top clients
    if data.get("topClients"):
        content.append(Paragraph("Top Klanten", styles["Heading2"]))
<<<<<<< HEAD:archive/packages/v1.00D/backend/routes/reports.py
        
        client_data = [["Naam", "E-mail", "Stad"]]
        for client in data["topClients"][:5]:
            client_data.append([
                client.get("name", ""),
                client.get("email", ""),
                client.get("city", "")
            ])
        
        client_table = Table(client_data, colWidths=[2*inch, 2.5*inch, 1.5*inch])
        client_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#10b981")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black)
        ]))
        
=======

        client_data = [["Naam", "E-mail", "Stad"]]
        for client in data["topClients"][:5]:
            client_data.append([client.get("name", ""), client.get("email", ""), client.get("city", "")])

        client_table = Table(client_data, colWidths=[2 * inch, 2.5 * inch, 1.5 * inch])
        client_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#10b981")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

>>>>>>> origin/main:packages/v1.00D/backend/routes/reports.py
        content.append(client_table)
        content.append(Spacer(1, 20))

    return content


def generate_clients_pdf_content(data, t, styles):
    """Generate clients report PDF content"""
    content = []
<<<<<<< HEAD:archive/packages/v1.00D/backend/routes/reports.py
    
    if data.get("topClientsByProjects"):
        content.append(Paragraph("Top Klanten op Projecten", styles["Heading2"]))
        
        client_data = [["Naam", "E-mail", "Projecten", "Totaal Budget"]]
        for client in data["topClientsByProjects"][:10]:
            client_data.append([
                client.get("name", ""),
                client.get("email", ""),
                str(client.get("projectCount", 0)),
                f"€{client.get('totalBudget', 0):,.2f}"
            ])
        
        client_table = Table(client_data, colWidths=[2*inch, 2*inch, 1*inch, 1.5*inch])
        client_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#10b981")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black)
        ]))
        
=======

    if data.get("topClientsByProjects"):
        content.append(Paragraph("Top Klanten op Projecten", styles["Heading2"]))

        client_data = [["Naam", "E-mail", "Projecten", "Totaal Budget"]]
        for client in data["topClientsByProjects"][:10]:
            client_data.append(
                [
                    client.get("name", ""),
                    client.get("email", ""),
                    str(client.get("projectCount", 0)),
                    f"€{client.get('totalBudget', 0):,.2f}",
                ]
            )

        client_table = Table(client_data, colWidths=[2 * inch, 2 * inch, 1 * inch, 1.5 * inch])
        client_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#10b981")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

>>>>>>> origin/main:packages/v1.00D/backend/routes/reports.py
        content.append(client_table)
        content.append(Spacer(1, 20))

    return content


def generate_projects_pdf_content(data, t, styles):
    """Generate projects report PDF content"""
    content = []

    # Project statistics
    content.append(Paragraph("Project Statistieken", styles["Heading2"]))
<<<<<<< HEAD:archive/packages/v1.00D/backend/routes/reports.py
    
    project_stats = [
        [t["total_projects"], str(data.get("totalProjects", 0))],
        [t["total_budget"], f"€{data.get('totalBudget', 0):,.2f}"],
        [t["average_budget"], f"€{data.get('averageBudget', 0):,.2f}"]
    ]
    
    stats_table = Table(project_stats, colWidths=[3*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black)
    ]))
    
=======

    project_stats = [
        [t["total_projects"], str(data.get("totalProjects", 0))],
        [t["total_budget"], f"€{data.get('totalBudget', 0):,.2f}"],
        [t["average_budget"], f"€{data.get('averageBudget', 0):,.2f}"],
    ]

    stats_table = Table(project_stats, colWidths=[3 * inch, 2 * inch])
    stats_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

>>>>>>> origin/main:packages/v1.00D/backend/routes/reports.py
    content.append(stats_table)
    content.append(Spacer(1, 20))

    # Status distribution
    if data.get("statusDistribution"):
        content.append(Paragraph("Status Verdeling", styles["Heading2"]))
<<<<<<< HEAD:archive/packages/v1.00D/backend/routes/reports.py
        
        status_data = [["Status", "Aantal"]]
        for status in data["statusDistribution"]:
            status_data.append([
                status.get("name", ""),
                str(status.get("value", 0))
            ])
        
        status_table = Table(status_data, colWidths=[3*inch, 2*inch])
        status_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#10b981")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black)
        ]))
        
=======

        status_data = [["Status", "Aantal"]]
        for status in data["statusDistribution"]:
            status_data.append([status.get("name", ""), str(status.get("value", 0))])

        status_table = Table(status_data, colWidths=[3 * inch, 2 * inch])
        status_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#10b981")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

>>>>>>> origin/main:packages/v1.00D/backend/routes/reports.py
        content.append(status_table)
        content.append(Spacer(1, 20))

    return content


def generate_plants_pdf_content(data, t, styles):
    """Generate plants report PDF content"""
    content = []

    # Plant statistics
    content.append(Paragraph("Plant Statistieken", styles["Heading2"]))
<<<<<<< HEAD:archive/packages/v1.00D/backend/routes/reports.py
    
    plant_stats = [
        [t["total_plants"], str(data.get("totalPlants", 0))],
        ["Inheemse Planten", str(data.get("nativePlants", 0))],
        ["Inheems Percentage", f"{data.get('nativePercentage', 0):.1f}%"]
    ]
    
    stats_table = Table(plant_stats, colWidths=[3*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black)
    ]))
    
=======

    plant_stats = [
        [t["total_plants"], str(data.get("totalPlants", 0))],
        ["Inheemse Planten", str(data.get("nativePlants", 0))],
        ["Inheems Percentage", f"{data.get('nativePercentage', 0):.1f}%"],
    ]

    stats_table = Table(plant_stats, colWidths=[3 * inch, 2 * inch])
    stats_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

>>>>>>> origin/main:packages/v1.00D/backend/routes/reports.py
    content.append(stats_table)
    content.append(Spacer(1, 20))

    # Category distribution
    if data.get("categoryDistribution"):
        content.append(Paragraph("Categorie Verdeling", styles["Heading2"]))
<<<<<<< HEAD:archive/packages/v1.00D/backend/routes/reports.py
        
        category_data = [["Categorie", "Aantal"]]
        for category in data["categoryDistribution"]:
            category_data.append([
                category.get("name", ""),
                str(category.get("value", 0))
            ])
        
        category_table = Table(category_data, colWidths=[3*inch, 2*inch])
        category_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#10b981")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black)
        ]))
        
=======

        category_data = [["Categorie", "Aantal"]]
        for category in data["categoryDistribution"]:
            category_data.append([category.get("name", ""), str(category.get("value", 0))])

        category_table = Table(category_data, colWidths=[3 * inch, 2 * inch])
        category_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#10b981")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

>>>>>>> origin/main:packages/v1.00D/backend/routes/reports.py
        content.append(category_table)
        content.append(Spacer(1, 20))

    return content


def generate_financial_pdf_content(data, t, styles):
    """Generate financial report PDF content"""
    content = []

    # Financial statistics
    content.append(Paragraph("Financiële Statistieken", styles["Heading2"]))
<<<<<<< HEAD:archive/packages/v1.00D/backend/routes/reports.py
    
    financial_stats = [
        ["Totale Omzet", f"€{data.get('totalRevenue', 0):,.2f}"],
        ["Voltooide Projecten", str(data.get("completedProjects", 0))],
        ["Gemiddelde Project Waarde", f"€{data.get('averageProjectValue', 0):,.2f}"]
    ]
    
    stats_table = Table(financial_stats, colWidths=[3*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black)
    ]))
    
=======

    financial_stats = [
        ["Totale Omzet", f"€{data.get('totalRevenue', 0):,.2f}"],
        ["Voltooide Projecten", str(data.get("completedProjects", 0))],
        ["Gemiddelde Project Waarde", f"€{data.get('averageProjectValue', 0):,.2f}"],
    ]

    stats_table = Table(financial_stats, colWidths=[3 * inch, 2 * inch])
    stats_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

>>>>>>> origin/main:packages/v1.00D/backend/routes/reports.py
    content.append(stats_table)
    content.append(Spacer(1, 20))

    # Monthly revenue
    if data.get("monthlyRevenue"):
        content.append(Paragraph("Maandelijkse Omzet", styles["Heading2"]))
<<<<<<< HEAD:archive/packages/v1.00D/backend/routes/reports.py
        
        revenue_data = [["Maand", "Omzet"]]
        for month_data in data["monthlyRevenue"]:
            revenue_data.append([
                month_data.get("month", ""),
                f"€{month_data.get('revenue', 0):,.2f}"
            ])
        
        revenue_table = Table(revenue_data, colWidths=[3*inch, 2*inch])
        revenue_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#10b981")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black)
        ]))
        
=======

        revenue_data = [["Maand", "Omzet"]]
        for month_data in data["monthlyRevenue"]:
            revenue_data.append([month_data.get("month", ""), f"€{month_data.get('revenue', 0):,.2f}"])

        revenue_table = Table(revenue_data, colWidths=[3 * inch, 2 * inch])
        revenue_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#10b981")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

>>>>>>> origin/main:packages/v1.00D/backend/routes/reports.py
        content.append(revenue_table)
        content.append(Spacer(1, 20))

    return content
