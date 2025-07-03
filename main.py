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
                    {"path": "su2.jpg"},
                    {"path": "raw29.png"},
                    {"path": "raw12.jpg"},
                    {"path": "su1.jpg"}
                ]
            }
        }

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

    # Specifications
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

    # Image Placement with debug logs and rect borders
    placements = {
        "raw12": (430, 690, 140, 110),  # Top-right
        "raw29": (60, 510, 300, 160),  # Left-middle
        "su2": (60, 320, 300, 160),  # Left-lower
        "su1": (60, 120, 300, 160)     # Left-bottom
    }

    script_dir = os.path.dirname(__file__)
    print("==== IMAGE DEBUG START ====")

    for img in data.images:
        print(f"\nProcessing image: {img.path}")
        basename = os.path.splitext(os.path.basename(img.path))[0]
        basename = basename.strip().replace(" ", "").lower()
        print(f" → Resolved basename: '{basename}'")

        if basename in placements:
            x, y, w, h = placements[basename]
            print(f" → Found in placements: ({x}, {y}, {w}, {h})")
        elif all([img.x, img.y, img.w, img.h]):
            x, y, w, h = img.x, img.y, img.w, img.h
            print(f" → Using custom coordinates: ({x}, {y}, {w}, {h})")
        else:
            print(f" ✗ No placement found and no coordinates provided for: {img.path}")
            continue

        image_path = img.path if os.path.isabs(img.path) else os.path.join(script_dir, img.path)
        print(f" → Final image path: {image_path}")

        try:
            if os.path.exists(image_path):
                c.drawImage(ImageReader(image_path), x, y, width=w, height=h, preserveAspectRatio=True)
                c.setStrokeColor(colors.grey)
                c.rect(x, y, w, h)  # Visual rectangle border
                print(f" ✓ Image added at ({x}, {y}, {w}, {h})")
            else:
                print(f" ✗ File not found: {image_path}")
        except Exception as e:
            print(f" ✗ Error rendering image '{img.path}': {e}")

    print("==== IMAGE DEBUG END ====")

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
