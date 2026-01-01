from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO


def generate_payslip_pdf(payroll_record):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    elements = [
        Paragraph("Payslip", styles["Title"]),
        Paragraph(f"Employee: {payroll_record.payee.full_name}", styles["Normal"]),
        Paragraph(f"Period: {payroll_record.payroll_period}", styles["Normal"]),
    ]

    table_data = [["Component", "Type", "Amount"]]

    for item in payroll_record.items.all():
        table_data.append([
            item.component_name,
            item.component_type,
            str(item.value),
        ])

    table_data.append(["Net Pay", "", str(payroll_record.net_pay)])

    elements.append(Table(table_data))
    doc.build(elements)

    return buffer.getvalue()
