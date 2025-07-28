# Reports API Routes
# File location: src/routes/reports.py
# This file handles all report generation operations

import io
from datetime import datetime

from flask import Blueprint, jsonify, request, send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

from src.models.landscape import (Client, Plant, Product, Project,
                                  ProjectPlant, Supplier, db)

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/api/reports/business-summary", methods=["GET"])
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

        status_distribution = {status: count for status, count in status_stats}

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
                db.func.count(ProjectPlant.project_id.distinct()).label(
                    "project_count"
                ),
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

        # Most used products - disabled for now as Product-Project relationship not directly modeled
        product_usage_data = []

        report_data = {
            "generated_at": datetime.utcnow().isoformat(),
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
                    "utilization_rate": (
                        (total_spent / total_budget * 100) if total_budget > 0 else 0
                    ),
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
                f"Generated: {datetime.utcnow().strftime('%B %d, %Y at %H:%M')}",
                styles["Normal"],
            )
        )
        if data["period"]["start_date"] and data["period"]["end_date"]:
            story.append(
                Paragraph(
                    f"Period: {data['period']['start_date']} to {data['period']['end_date']}",
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
                        (
                            f"€{client['total_budget']:,.2f}"
                            if client["total_budget"]
                            else "€0.00"
                        ),
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
            download_name=f'business_summary_{datetime.utcnow().strftime("%Y%m%d")}.pdf',
            mimetype="application/pdf",
        )

    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500


@reports_bp.route("/api/reports/project/<int:project_id>", methods=["GET"])
def generate_project_report(project_id):
    """Generate detailed project report"""
    try:
        format_type = request.args.get("format", "json")  # json or pdf

        project = Project.query.get_or_404(project_id)

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

        # Get project products with details - disabled as no direct Product-Project relationship
        products_data = []
        total_product_cost = 0

        report_data = {
            "generated_at": datetime.utcnow().isoformat(),
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "budget": float(project.budget) if project.budget else 0,
                "spent": 0,  # No spent field in current model
                "location": project.location,
                "area_size": (float(project.area_size) if project.area_size else 0),
                "start_date": (
                    project.start_date.isoformat() if project.start_date else None
                ),
                "end_date": (
                    project.end_date.isoformat() if project.end_date else None
                ),
                "notes": project.notes,
                "created_at": (
                    project.created_at.isoformat() if project.created_at else None
                ),
            },
            "client": {
                "name": project.client.name,
                "email": project.client.email,
                "phone": project.client.phone,
                "client_type": project.client.client_type,
                "address": project.client.address,
                "city": project.client.city,
                "postal_code": project.client.postal_code,
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
            download_name=f'project_{project["name"].replace(" ", "_")}_{datetime.utcnow().strftime("%Y%m%d")}.pdf',
            mimetype="application/pdf",
        )

    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500


@reports_bp.route("/api/reports/plant-usage", methods=["GET"])
def generate_plant_usage_report():
    """Generate plant usage statistics report"""
    try:
        # Get plant usage statistics
        plant_usage = (
            db.session.query(
                Plant.name,
                Plant.scientific_name,
                Plant.category,
                db.func.count(db.distinct(Project.id)).label("project_count"),
            )
            .join(Project.plants)
            .join(Project)
            .group_by(Plant.id, Plant.name, Plant.scientific_name, Plant.category)
            .order_by(db.desc("project_count"))
            .all()
        )

        usage_data = []
        for name, scientific_name, category, count in plant_usage:
            usage_data.append(
                {
                    "name": name,
                    "scientific_name": scientific_name,
                    "category": category,
                    "project_count": count,
                }
            )

        # Category distribution
        category_stats = (
            db.session.query(
                Plant.category,
                db.func.count(db.distinct(Project.id)).label("project_count"),
            )
            .join(Project.plants)
            .join(Project)
            .filter(Plant.category.isnot(None))
            .group_by(Plant.category)
            .order_by(db.desc("project_count"))
            .all()
        )

        category_distribution = {category: count for category, count in category_stats}

        return jsonify(
            {
                "generated_at": datetime.utcnow().isoformat(),
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
                db.func.count(Product.id).label("product_count"),
                db.func.count(db.distinct(Project.id)).label("project_count"),
            )
            .outerjoin(Product)
            .outerjoin(Project.products)
            .outerjoin(Project)
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
                "generated_at": datetime.utcnow().isoformat(),
                "suppliers": supplier_data,
                "total_suppliers": len(supplier_data),
                "top_supplier": supplier_data[0] if supplier_data else None,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
