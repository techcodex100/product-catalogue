from fastapi import FastAPI, Response
from pydantic import BaseModel
from typing import List, Optional
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from io import BytesIO
import threading
import os

app = FastAPI()
lock = threading.Lock()
COUNTER_FILE = "counter.txt"


class ImageData(BaseModel):
    path: str
    x: float
    y: float
    w: float
    h: float

class ProductData(BaseModel):
    name: str
    hs_code: Optional[str] = ""
    quantity: Optional[str] = ""
    unit: Optional[str] = ""
    fcl_type: Optional[str] = ""
    packaging: Optional[str] = ""
    quantity_per_fcl: Optional[str] = ""
    description: List[str] = []
    specifications: List[str] = []
    images: List[ImageData] = []

def get_next_counter():
    with lock:
        if not os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, "w") as f:
                f.write("1")
            return 1
        with open(COUNTER_FILE, "r+") as f:
            count = int(f.read())
            f.seek(0)
            f.write(str(count + 1))
            f.truncate()
            return count

@app.get("/")
def home():
    return {"message": "Codex Catalog PDF Generator is running. Use POST /generate-catalog-pdf"}

@app.post("/generate-catalog-pdf/")
async def generate_catalog_pdf(data: ProductData):
    pdf_number = get_next_counter()
    filename = f"Catalog_{pdf_number}.pdf"
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.grey)
    c.drawString(40, height - 30, "docwise.codexautomationkey.com")
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.black)
    c.drawRightString(width - 40, height - 30, "CODEX AUTOMATION KEY")
    c.setFont("Helvetica", 8)
    c.drawRightString(width - 40, height - 43, "Product Catalog")

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2, height - 80, data.name.upper())

    # Product Info
    y_info = height - 110
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y_info, "PRODUCT DETAILS:")
    y_info -= 15
    c.setFont("Helvetica", 9)
    fields = [
        ("HS Code", data.hs_code),
        ("Quantity", data.quantity),
        ("Unit", data.unit),
        ("FCL Type", data.fcl_type),
        ("Packaging", data.packaging),
        ("Quantity per FCL", data.quantity_per_fcl)
    ]
    for label, value in fields:
        if value:
            c.drawString(50, y_info, f"{label}: {value}")
            y_info -= 13

    # Description
    y_desc = y_info - 20
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y_desc, "DESCRIPTION:")
    y_desc -= 15
    c.setFont("Helvetica", 9)
    for line in data.description:
        c.drawString(50, y_desc, line)
        y_desc -= 13

    # Specifications (Bottom-Right Box)
    spec_x = width - 200
    spec_y = 490
    if data.specifications:
        c.setFont("Helvetica-Bold", 10)
        c.drawString(spec_x, spec_y, "SPECIFICATIONS:")
        spec_y -= 15
        c.setFont("Helvetica", 9)
        for spec in data.specifications:
            c.drawString(spec_x + 10, spec_y, f"• {spec}")
            spec_y -= 12

    # Images
    placements = {
        "su2.jpg": (430, 690, 140, 110),       # Top-right image — slightly larger
        "raw29.jpg": (60, 370, 300, 160),     # Center main image — wider & taller
        "raw12.jpg": (400, 140, 140, 90),     # Bottom-left logo — bigger but still balanced
        "su1.jpg": ( 40, 160, 350, 160)         # Centered above footer
    }
    for label, (x, y, w, h) in placements.items():
        for img in data.images:
            if img.path == label and os.path.exists(img.path):
                try:
                    c.drawImage(ImageReader(img.path), x, y, width=w, height=h, preserveAspectRatio=True)
                except Exception as e:
                    print(f"Image error ({label}):", e)

    # Footer
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, 30, "Codex Automation Key, Indore, M.P., India")
    c.drawCentredString(width / 2, 18, "Tel: (+91) 731 2515151 • Email: info@codexautomationkey.com")

    # Finalize PDF
    c.save()
    buffer.seek(0)
    return Response(
        content=buffer.read(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
