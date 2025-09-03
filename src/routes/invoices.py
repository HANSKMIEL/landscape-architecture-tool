# Invoice and Quote Generation API Routes
# File location: src/routes/invoices.py
# This file handles invoice and quote generation operations

import io
import logging
from datetime import UTC, datetime
from decimal import Decimal

from flask import Blueprint, jsonify, request, send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import or_

from src.models.landscape import Project, db
from src.routes.user import data_access_required

invoices_bp = Blueprint("invoices", __name__)

# Company information for invoices
COMPANY_INFO = {
    "name": "HANSKMIEL Landschapsarchitectuur",
    "address": "Groene Laan 123",
    "city": "1234 AB Amsterdam",
    "phone": "+31 (0)20 123 4567",
    "email": "info@hanskmiel.nl",
    "website": "www.hanskmiel.nl",
    "vat_number": "NL123456789B01",
    "bank_account": "NL12 ABCD 0123 4567 89",
}


@invoices_bp.route("/invoices/quote/<int:project_id>", methods=["GET"])
@data_access_required
def generate_quote(project_id):
    """Generate quote for a project"""
    try:
        format_type = request.args.get("format", "json")  # json or pdf

        project = db.session.get(Project, project_id)
        if not project:
            return jsonify({"error": "Project niet gevonden"}), 404

        # Calculate quote items
        quote_items = []
        subtotal = Decimal("0")

        # Add plants with pricing
        for project_plant in project.project_plants:
            plant = project_plant.plant
            if plant:
                quantity = project_plant.quantity or 1
                unit_cost = Decimal(str(project_plant.unit_cost or 0))
                line_total = quantity * unit_cost

                quote_items.append(
                    {
                        "type": "plant",
                        "description": f"{plant.name} ({plant.common_name or 'Tuinplant'})",
                        "quantity": quantity,
                        "unit": "stuks",
                        "unit_price": float(unit_cost),
                        "total": float(line_total),
                        "category": plant.category or "Beplanting",
                    }
                )
                subtotal += line_total

        # Add project-specific services
        if project.area_size:
            area_rate = Decimal("25.00")  # €25 per m² for design
            design_cost = Decimal(str(project.area_size)) * area_rate
            quote_items.append(
                {
                    "type": "service",
                    "description": f"Tuinontwerp en planning ({project.area_size} m²)",
                    "quantity": float(project.area_size),
                    "unit": "m²",
                    "unit_price": float(area_rate),
                    "total": float(design_cost),
                    "category": "Ontwerp",
                }
            )
            subtotal += design_cost

        # Add consultation fee
        consultation_fee = Decimal("150.00")
        quote_items.append(
            {
                "type": "service",
                "description": "Locatiebezoek en adviesgesprek",
                "quantity": 1,
                "unit": "uur",
                "unit_price": float(consultation_fee),
                "total": float(consultation_fee),
                "category": "Advies",
            }
        )
        subtotal += consultation_fee

        # Calculate taxes and totals
        vat_rate = Decimal("0.21")  # 21% BTW
        vat_amount = subtotal * vat_rate
        total_amount = subtotal + vat_amount

        quote_data = {
            "quote_number": f"OFF-{project.id:04d}-{datetime.now(UTC).strftime('%Y%m')}",
            "generated_at": datetime.now(UTC).isoformat(),
            "valid_until": (
                datetime.now(UTC).replace(day=1, month=datetime.now().month + 1)
                if datetime.now().month < 12
                else datetime.now(UTC).replace(year=datetime.now().year + 1, month=1, day=1)
            ).isoformat(),
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "location": project.location,
                "area_size": float(project.area_size) if project.area_size else 0,
            },
            "client": {
                "name": project.client.name if project.client else "Onbekende klant",
                "email": project.client.email if project.client else "",
                "phone": project.client.phone if project.client else "",
                "address": project.client.address if project.client else "",
                "city": project.client.city if project.client else "",
                "postal_code": project.client.postal_code if project.client else "",
            },
            "items": quote_items,
            "financial": {
                "subtotal": float(subtotal),
                "vat_rate": float(vat_rate),
                "vat_amount": float(vat_amount),
                "total": float(total_amount),
                "currency": "EUR",
            },
            "company": COMPANY_INFO,
        }

        if format_type == "pdf":
            return generate_quote_pdf(quote_data)

        return jsonify(quote_data)

    except Exception as e:
        logging.exception("Error generating quote")
        return jsonify({"error": f"Fout bij genereren offerte: {e!s}"}), 500


def generate_quote_pdf(data):
    """Generate PDF version of quote"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5 * inch)
        styles = getSampleStyleSheet()
        story = []

        # Header with company info
        header_table_data = [
            [
                Paragraph(
                    f"<b>{COMPANY_INFO['name']}</b><br/>"
                    f"{COMPANY_INFO['address']}<br/>"
                    f"{COMPANY_INFO['city']}<br/>"
                    f"Tel: {COMPANY_INFO['phone']}<br/>"
                    f"Email: {COMPANY_INFO['email']}",
                    styles["Normal"],
                ),
                Paragraph(
                    f"<b>OFFERTE</b><br/>"
                    f"Nummer: {data['quote_number']}<br/>"
                    f"Datum: {datetime.now(UTC).strftime('%d-%m-%Y')}<br/>"
                    f"Geldig tot: {datetime.fromisoformat(data['valid_until']).strftime('%d-%m-%Y')}",
                    styles["Normal"],
                ),
            ]
        ]

        header_table = Table(header_table_data, colWidths=[3 * inch, 2.5 * inch])
        header_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ]
            )
        )
        story.append(header_table)
        story.append(Spacer(1, 30))

        # Client information
        client = data["client"]
        story.append(Paragraph("<b>Klantgegevens:</b>", styles["Heading3"]))
        client_text = f"{client['name']}"
        if client["address"]:
            client_text += f"<br/>{client['address']}"
        if client["postal_code"] or client["city"]:
            client_text += f"<br/>{client['postal_code']} {client['city']}"
        if client["phone"]:
            client_text += f"<br/>Tel: {client['phone']}"
        if client["email"]:
            client_text += f"<br/>Email: {client['email']}"

        story.append(Paragraph(client_text, styles["Normal"]))
        story.append(Spacer(1, 20))

        # Project information
        project = data["project"]
        story.append(Paragraph("<b>Projectgegevens:</b>", styles["Heading3"]))
        story.append(Paragraph(f"Project: {project['name']}", styles["Normal"]))
        if project["location"]:
            story.append(Paragraph(f"Locatie: {project['location']}", styles["Normal"]))
        if project["area_size"]:
            story.append(Paragraph(f"Oppervlakte: {project['area_size']} m²", styles["Normal"]))
        if project["description"]:
            story.append(Paragraph(f"Omschrijving: {project['description']}", styles["Normal"]))
        story.append(Spacer(1, 30))

        # Quote items table
        story.append(Paragraph("<b>Offerte onderdelen:</b>", styles["Heading3"]))

        items_data = [["Omschrijving", "Aantal", "Eenheid", "Prijs per eenheid", "Totaal"]]

        for item in data["items"]:
            items_data.append(
                [
                    item["description"],
                    str(item["quantity"]),
                    item["unit"],
                    f"€ {item['unit_price']:.2f}",
                    f"€ {item['total']:.2f}",
                ]
            )

        items_table = Table(items_data, colWidths=[2.5 * inch, 0.8 * inch, 0.8 * inch, 1.2 * inch, 1.2 * inch])
        items_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2D5016")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 0), (-1, -1), "RIGHT"),  # Right align numbers
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(items_table)
        story.append(Spacer(1, 20))

        # Financial summary
        financial = data["financial"]
        summary_data = [
            ["Subtotaal", f"€ {financial['subtotal']:.2f}"],
            [f"BTW ({financial['vat_rate']*100:.0f}%)", f"€ {financial['vat_amount']:.2f}"],
            ["", ""],
            ["TOTAAL", f"€ {financial['total']:.2f}"],
        ]

        summary_table = Table(summary_data, colWidths=[4 * inch, 1.5 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 3), (1, 3), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 3), (1, 3), 12),
                    ("LINEABOVE", (0, 3), (1, 3), 2, colors.black),
                    ("BACKGROUND", (0, 3), (1, 3), colors.lightgrey),
                ]
            )
        )
        story.append(summary_table)
        story.append(Spacer(1, 30))

        # Terms and conditions
        story.append(Paragraph("<b>Voorwaarden:</b>", styles["Heading3"]))
        terms = [
            "• Deze offerte is geldig tot de aangegeven datum",
            "• Prijzen zijn inclusief 21% BTW",
            "• Betaling binnen 30 dagen na factuurdatum",
            "• Aanvullende kosten voor onvoorziene werkzaamheden worden vooraf gecommuniceerd",
            "• Acceptatie van deze offerte geldt als opdrachtverlening",
        ]
        for term in terms:
            story.append(Paragraph(term, styles["Normal"]))

        story.append(Spacer(1, 20))

        # Footer
        story.append(Paragraph(f"BTW nummer: {COMPANY_INFO['vat_number']}", styles["Normal"]))
        story.append(Paragraph(f"Bankrekening: {COMPANY_INFO['bank_account']}", styles["Normal"]))

        doc.build(story)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'offerte_{data["quote_number"]}_{datetime.now(UTC).strftime("%Y%m%d")}.pdf',
            mimetype="application/pdf",
        )

    except Exception as e:
        logging.exception("Error generating quote PDF")
        return jsonify({"error": f"Fout bij genereren offerte PDF: {e!s}"}), 500


@invoices_bp.route("/api/invoices/invoice/<int:project_id>", methods=["POST"])
@data_access_required
def generate_invoice(project_id):
    """Generate invoice for a project (converts quote to invoice)"""
    try:
        data = request.get_json() or {}
        format_type = data.get("format", "json")

        project = db.session.get(Project, project_id)
        if not project:
            return jsonify({"error": "Project niet gevonden"}), 404

        # Get quote data first
        quote_response = generate_quote(project_id)
        if quote_response[1] != 200:  # Error case
            return quote_response

        quote_data = quote_response[0].get_json()

        # Convert quote to invoice
        invoice_data = quote_data.copy()
        invoice_data.update(
            {
                "invoice_number": f"FACT-{project.id:04d}-{datetime.now(UTC).strftime('%Y%m')}",
                "invoice_date": datetime.now(UTC).isoformat(),
                "due_date": (datetime.now(UTC).replace(day=datetime.now().day + 30)).isoformat(),
                "payment_terms": "30 dagen",
                "type": "invoice",
            }
        )

        # Remove quote-specific fields
        invoice_data.pop("quote_number", None)
        invoice_data.pop("valid_until", None)

        if format_type == "pdf":
            return generate_invoice_pdf(invoice_data)

        return jsonify(invoice_data)

    except Exception as e:
        logging.exception("Error generating invoice")
        return jsonify({"error": f"Fout bij genereren factuur: {e!s}"}), 500


def generate_invoice_pdf(data):
    """Generate PDF version of invoice"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5 * inch)
        styles = getSampleStyleSheet()
        story = []

        # Header with company info
        header_table_data = [
            [
                Paragraph(
                    f"<b>{COMPANY_INFO['name']}</b><br/>"
                    f"{COMPANY_INFO['address']}<br/>"
                    f"{COMPANY_INFO['city']}<br/>"
                    f"Tel: {COMPANY_INFO['phone']}<br/>"
                    f"Email: {COMPANY_INFO['email']}",
                    styles["Normal"],
                ),
                Paragraph(
                    f"<b>FACTUUR</b><br/>"
                    f"Nummer: {data['invoice_number']}<br/>"
                    f"Datum: {datetime.fromisoformat(data['invoice_date']).strftime('%d-%m-%Y')}<br/>"
                    f"Vervaldatum: {datetime.fromisoformat(data['due_date']).strftime('%d-%m-%Y')}",
                    styles["Normal"],
                ),
            ]
        ]

        header_table = Table(header_table_data, colWidths=[3 * inch, 2.5 * inch])
        header_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ]
            )
        )
        story.append(header_table)
        story.append(Spacer(1, 30))

        # Client information
        client = data["client"]
        story.append(Paragraph("<b>Klantgegevens:</b>", styles["Heading3"]))
        client_text = f"{client['name']}"
        if client["address"]:
            client_text += f"<br/>{client['address']}"
        if client["postal_code"] or client["city"]:
            client_text += f"<br/>{client['postal_code']} {client['city']}"
        if client["phone"]:
            client_text += f"<br/>Tel: {client['phone']}"
        if client["email"]:
            client_text += f"<br/>Email: {client['email']}"

        story.append(Paragraph(client_text, styles["Normal"]))
        story.append(Spacer(1, 20))

        # Project information
        project = data["project"]
        story.append(Paragraph("<b>Projectgegevens:</b>", styles["Heading3"]))
        story.append(Paragraph(f"Project: {project['name']}", styles["Normal"]))
        if project["location"]:
            story.append(Paragraph(f"Locatie: {project['location']}", styles["Normal"]))
        if project["description"]:
            story.append(Paragraph(f"Omschrijving: {project['description']}", styles["Normal"]))
        story.append(Spacer(1, 30))

        # Invoice items table
        story.append(Paragraph("<b>Factuur onderdelen:</b>", styles["Heading3"]))

        items_data = [["Omschrijving", "Aantal", "Eenheid", "Prijs per eenheid", "Totaal"]]

        for item in data["items"]:
            items_data.append(
                [
                    item["description"],
                    str(item["quantity"]),
                    item["unit"],
                    f"€ {item['unit_price']:.2f}",
                    f"€ {item['total']:.2f}",
                ]
            )

        items_table = Table(items_data, colWidths=[2.5 * inch, 0.8 * inch, 0.8 * inch, 1.2 * inch, 1.2 * inch])
        items_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2D5016")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 0), (-1, -1), "RIGHT"),  # Right align numbers
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(items_table)
        story.append(Spacer(1, 20))

        # Financial summary
        financial = data["financial"]
        summary_data = [
            ["Subtotaal", f"€ {financial['subtotal']:.2f}"],
            [f"BTW ({financial['vat_rate']*100:.0f}%)", f"€ {financial['vat_amount']:.2f}"],
            ["", ""],
            ["TE BETALEN", f"€ {financial['total']:.2f}"],
        ]

        summary_table = Table(summary_data, colWidths=[4 * inch, 1.5 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 3), (1, 3), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 3), (1, 3), 12),
                    ("LINEABOVE", (0, 3), (1, 3), 2, colors.black),
                    ("BACKGROUND", (0, 3), (1, 3), colors.lightgrey),
                ]
            )
        )
        story.append(summary_table)
        story.append(Spacer(1, 30))

        # Payment information
        story.append(Paragraph("<b>Betaalinformatie:</b>", styles["Heading3"]))
        payment_info = [
            f"• Betaaltermijn: {data['payment_terms']}",
            f"• Bankrekening: {COMPANY_INFO['bank_account']}",
            f"• Onder vermelding van factuurnummer: {data['invoice_number']}",
            "• Voor vragen kunt u contact opnemen via bovenstaande gegevens",
        ]
        for info in payment_info:
            story.append(Paragraph(info, styles["Normal"]))

        story.append(Spacer(1, 20))

        # Footer
        story.append(Paragraph(f"BTW nummer: {COMPANY_INFO['vat_number']}", styles["Normal"]))

        doc.build(story)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'factuur_{data["invoice_number"]}_{datetime.now(UTC).strftime("%Y%m%d")}.pdf',
            mimetype="application/pdf",
        )

    except Exception as e:
        logging.exception("Error generating invoice PDF")
        return jsonify({"error": f"Fout bij genereren factuur PDF: {e!s}"}), 500


@invoices_bp.route("/api/invoices/projects", methods=["GET"])
@data_access_required
def list_invoiceable_projects():
    """List projects that can be invoiced"""
    try:
        # Handle both Dutch and English status values
        completed_statuses = ["completed", "Afgerond", "afgerond"]
        in_progress_statuses = ["in_progress", "In uitvoering", "in_uitvoering"]

        projects = Project.query.filter(
            or_(Project.status.in_(completed_statuses), Project.status.in_(in_progress_statuses))
        ).all()

        invoiceable_projects = []
        for project in projects:
            invoiceable_projects.append(
                {
                    "id": project.id,
                    "name": project.name,
                    "client_name": project.client.name if project.client else "Onbekende klant",
                    "status": project.status,
                    "budget": float(project.budget) if project.budget else 0,
                    "area_size": float(project.area_size) if project.area_size else 0,
                    "plant_count": len(project.project_plants),
                    "created_at": project.created_at.isoformat() if project.created_at else None,
                }
            )

        return jsonify({"projects": invoiceable_projects, "total": len(invoiceable_projects)})

    except Exception as e:
        logging.exception("Error listing invoiceable projects")
        return jsonify({"error": f"Fout bij ophalen projecten: {e!s}"}), 500
