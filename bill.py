from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import os
import subprocess
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_pdf(file_name, text_list):
    # Create a PDF canvas
    c = canvas.Canvas(file_name, pagesize=letter)

    # Set font and font size
    c.setFont("Helvetica", 12)

    # Set the starting position for the text
    x, y = 100, 700

    # Add each element from the text_list on a new line
    for text in text_list:
        c.drawString(x, y, text)
        y -= 20  # Move to the next line, adjust this value as needed

    # Save the PDF and close the canvas
    c.save()

def create_bill(file_path, bill_data, total_amount):
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    elements = []
    elements.append(Table([['', '', '', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]]))
    # Create the table data (you can customize this based on your bill data)
    table_data = [bill_data[0].keys()]

    for row in bill_data:
        table_data.append([i for i in row.values()])

    # Add the table to the elements list
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    # Add total amount at the end
    elements.append(Table([['', '', '', f'Total: {total_amount:.2f}DA']]))

    # Build the PDF
    doc.build(elements)

def open_pdf(file_path):
    if os.path.exists(file_path):
        if os.name == 'nt':
            os.startfile(file_path)  # For Windows
        else:
            subprocess.Popen(['xdg-open', file_path])  # For Linux

if __name__ == "__main__":
    bill_data = [
        ("Item 1", 5, 10),
        ("Item 2", 2, 15),
        ("Item 3", 3, 8),
    ]

    pdf_file_path = "bill.pdf"

    # Create the bill as a PDF
    create_bill(pdf_file_path, bill_data)

    # Open the PDF
    open_pdf(pdf_file_path)
