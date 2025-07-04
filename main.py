from fastapi import FastAPI, Response, Request
from pydantic import BaseModel
from typing import List, Optional
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from io import BytesIO
import threading
import os
from datetime import datetime  # ✅ Added for unique filename

app = FastAPI()
lock = threading.Lock()
COUNTER_FILE = "counter.txt"

class ImageData(BaseModel):
    path: str
    x: Optional[float] = None
    y: Optional[float] = None
    w: Optional[float] = None
    h: Optional[float] = None

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

    class Config:
        schema_extra = {
            "example": {
                "name": "Zinc Oxide",
                "hs_code": "28170010",
                "quantity": "500",
                "unit": "KG",
                "fcl_type": "20 FCL",
                "packaging": "HDPE Bags",
                "quantity_per_fcl": "24 MT",
                "description": [
                    "White powdered compound used in rubber, ceramics, and cosmetics.",
                    "High purity, low lead content, suitable for industrial applications."
                ],
                "specifications": [
                    "Purity: 99.7%",
                    "Particle Size: < 5 microns",
                    "Lead Content: < 0.001%"
                ],
                "images": [
                    { "path": "su2.jpg" },
                    { "path": "raw29.png" },
                    { "path": "raw12.jpeg" },
                    { "path": "su1.jpg" }
                ]
            }
        }

@app.middleware("http")
async def log_request(request: Request, call_next):
    body = await request.body()
    print("Incoming Request Body:", body.decode())
    return await call_next(request)

@app.get("/")
def home():
    return {"message": "Codex Catalog PDF Generator is running. Use POST /generate-catalog-pdf"}

@app.post("/generate-catalog-pdf/")
async def generate_catalog_pdf(data: ProductData):
    # ✅ Use timestamp for unique filename
    filename = f"Catalog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
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

    # Description section (replacing product details)
    y_desc = height - 110
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y_desc, "DESCRIPTION:")
    y_desc -= 15
    c.setFont("Helvetica", 9)
    for line in data.description:
        c.drawString(50, y_desc, line)
        y_desc -= 13

    # Image placements
    placements = {
        "raw29": (60, 480, 300, 160),
        "su2":   (60, 290, 300, 160),
        "su1":   (60, 100, 300, 160)
    }

    script_dir = os.path.dirname(__file__)
    MAX_WIDTH = 300
    MAX_HEIGHT = 200

    for img in data.images:
        basename = os.path.splitext(os.path.basename(img.path))[0].strip().replace(" ", "").lower()

        if basename in placements:
            x, y, w, h = placements[basename]
        elif all([img.x, img.y, img.w, img.h]):
            x, y, w, h = img.x, img.y, img.w, img.h
        else:
            print(f"No placement defined for: {img.path}")
            continue

        scale = min(MAX_WIDTH / w, MAX_HEIGHT / h, 1.0)
        w_scaled = w * scale
        h_scaled = h * scale

        image_path = img.path if os.path.isabs(img.path) else os.path.join(script_dir, img.path)

        try:
            if os.path.exists(image_path):
                c.drawImage(ImageReader(image_path), x, y, width=w_scaled, height=h_scaled, preserveAspectRatio=True)
                print(f"✅ Image added: {basename} at ({x}, {y}, {w_scaled}, {h_scaled})")
            else:
                print(f"❌ File not found: {image_path}")
        except Exception as e:
            print(f"⚠️ Image error ({image_path}): {e}")

    # Product Details + Specifications section at the bottom
    bottom_y = 280
    c.setFont("Helvetica-Bold", 10)
    c.drawString(width - 200, bottom_y, "PRODUCT DETAILS:")
    bottom_y -= 15
    c.setFont("Helvetica", 9)

    details = [
        ("HS Code", data.hs_code),
        ("Quantity", data.quantity),
        ("Unit", data.unit),
        ("FCL Type", data.fcl_type),
        ("Packaging", data.packaging),
        ("Quantity per FCL", data.quantity_per_fcl)
    ]
    for label, value in details:
        if value:
            c.drawString(width - 190, bottom_y, f"{label}: {value}")
            bottom_y -= 12

    for spec in data.specifications:
        c.drawString(width - 190, bottom_y, f"• {spec}")
        bottom_y -= 12

    # Footer
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, 30, "Codex Automation Key, Indore, M.P., India")
    c.drawCentredString(width / 2, 18, "Tel: (+91) 731 2515151 • Email: info@codexautomationkey.com")

    c.save()
    buffer.seek(0)
    return Response(
        content=buffer.read(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
