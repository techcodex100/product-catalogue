from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import os

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="catalog_images"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate-pdf")
async def generate_catalog():
    output_pdf = "company_catalog.pdf"
    image_folder = "C:\\Users\\Lenovo\\OneDrive\\Desktop\\finalcatalog\\templates\\catalog_images"

    pages = [
        "C:\\Users\\Lenovo\\OneDrive\\Desktop\\finalcatalog\\1.jpg",
        "C:\\Users\\Lenovo\\OneDrive\\Desktop\\finalcatalog\\2.png",
        "C:\\Users\\Lenovo\\OneDrive\\Desktop\\finalcatalog\\3.png",
        "C:\\Users\\Lenovo\\OneDrive\\Desktop\\finalcatalog\\4.png",
        "C:\\Users\\Lenovo\\OneDrive\\Desktop\\finalcatalog\\5.png",
        "C:\\Users\\Lenovo\\OneDrive\\Desktop\\finalcatalog\\6.png",
        "C:\\Users\\Lenovo\\OneDrive\\Desktop\\finalcatalog\\7.png"
    ]

    c = canvas.Canvas(output_pdf, pagesize=A4)
    width, height = A4

    for index, page_filename in enumerate(pages):
        img_path = os.path.join(image_folder, page_filename)

        if os.path.exists(img_path):
            c.drawImage(img_path, 0, 0, width=width, height=height)
        else:
            c.setFont("Helvetica", 12)
            c.setFillColor(colors.red)
            c.drawString(100, height - 100, f"Missing image: {page_filename}")

        if index == 0:
            c.setFont("Helvetica-Bold", 30)
            c.setFillColor(colors.white)
            c.drawCentredString(width / 2, height - 200, "CODEX AUTOMATION KEY")
            c.setFont("Helvetica", 20)
            c.drawCentredString(width / 2, height - 230, "COMPANY CATALOG")

        if index == 1:
            c.setFont("Helvetica-Bold", 24)
            c.setFillColor(colors.darkblue)
            c.drawCentredString(width / 2, height - 50, "ABOUT US")
            about_text = (
                "Codex Automation Key stands as a symbol of innovation, precision, \n and excellence in"
                "the field of industrial automation.\n \n"
                "We cater to a wide range of sectors, delivering tailor-made solutions that align\n"
                "with evolving industry needs and global standards.\n \n "
                "• Expertise across multiple domains with efficient and innovative products.\n \n "
                "• Integration of advanced sensors, industrial controllers, and automation solutions.\n \n "
                "• Focus on enhancing productivity, safety, and operational efficiency.\n \n "
                "• Customized solutions from a dedicated team of engineers and professionals."
            )
            text_obj = c.beginText(20, 300)
            text_obj.setFont("Helvetica", 15.7)
            text_obj.setFillColor(colors.black)
            for line in about_text.split("\n"):
                text_obj.textLine(line)
            c.drawText(text_obj)

        if index == 2:
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 24)
            c.drawRightString(520, 790, "PRODUCT LIST")
            c.setFont("Helvetica-Bold", 14)
            c.drawRightString(450, 725, "• RAW SUGAR")
            c.drawRightString(450, 475, "• CHICKPEAS")
            c.drawRightString(480, 275, "• REFINED SUGAR")

        if index == 3:
            c.setFont("Helvetica-Bold", 24)
            c.setFillColor(colors.darkred)
            c.drawString(50, 800, "RAW SUGAR")
            c.setFont("Helvetica-Bold", 15)
            c.setFillColor(colors.black)
            description_text = (
                "\n Description:\n \n "
                "• Raw sugar is partially refined sugar with \n natural molasses content, \n giving it a distinct color and flavor.\n"
                "• It serves as a crucial intermediate product \n in sugar refining industries and is also \n used in bakeries,"
                "confectioneries, and \n certain specialty food products.\n"
                "• Its versatility makes it suitable for both \n industrial and limited direct consumption."
            )
            desc_obj = c.beginText(50, 780)
            desc_obj.setFont("Helvetica-Bold", 13)
            for line in description_text.split("\n"):
                desc_obj.textLine(line)
            c.drawText(desc_obj)
            spec_text = (
                "Specifications:\n \n "
                "• Brownish crystals\n"
                "• Color: Light Brown\n"
                "• Moisture: Max 0.10%\n"
                "• Polarity: 98.50% Min\n"
                "• ICUMSA: 600-1200\n"
                "• Ash Content: Max 0.25%\n"
                "• Grain Size: Medium\n"
                "• HS Code: 1709671"
            )
            spec_obj = c.beginText(350, 500)
            spec_obj.setFont("Helvetica-Bold", 17)
            for line in spec_text.split("\n"):
                spec_obj.textLine(line)
            c.drawText(spec_obj)

        if index == 4:
            c.setFont("Helvetica-Bold", 24)
            c.setFillColor(colors.darkred)
            c.drawString(50, 800, "REFINED SUGAR")
            c.setFont("Helvetica-Bold", 15)
            c.setFillColor(colors.black)
            description_text = (
                "\n Description:\n \n "
                "• Refined sugar, also known as white sugar, \n is the most"
                " commonly used sweetener.\n"
                "• It is produced through a multi-stage \n purification process"
                " that removes molasses, \n and color, resulting"
                " in pure sucrose crystals.\n"
                "• Refined sugar adheres to stringent quality \n standards"
                " ensuring optimal taste, texture,\n and hygiene.\n"
                "• Its long shelf life and high purity make it a \n key ingredient in"
                " various international market."
            )
            desc_obj = c.beginText(50, 780)
            desc_obj.setFont("Helvetica-Bold", 12.6)
            for line in description_text.split("\n"):
                desc_obj.textLine(line)
            c.drawText(desc_obj)
            spec_text = (
                "Specifications:\n \n "
                "• White crystals\n"
                "• HS Code: 170190\n"
                "• Type: Human Consumption\n"
                "• ICUMSA Rating: 45 RBU\n"
                "• Color: Sparkling White\n"
                "• Polarity: 99.80% Minimum\n"
                "• Moisture: 0.04% Maximum"
            )
            spec_obj = c.beginText(350, 500)
            spec_obj.setFont("Helvetica-Bold", 17)
            for line in spec_text.split("\n"):
                spec_obj.textLine(line)
            c.drawText(spec_obj)

        if index == 5:
            c.setFont("Helvetica-Bold", 24)
            c.setFillColor(colors.darkred)
            c.drawString(50, 800, "CHICKPEAS")
            c.setFont("Helvetica-Bold", 15)
            c.setFillColor(colors.black)
            description_text = (
                "\n Description:\n \n "
                "• Chickpeas, also known as Garbanzo Beans, \n are a highly nutritious legume cultivated and \n consumed worldwide. \n"
                "• They are a rich source of plant-based protein, \n dietary fiber, vitamins (such as B6, folate), and \n essential minerals"
                " including iron, magnesium.\n"
                "• Strict quality control measures ensure proper \n sorting, cleaning, drying, and packaging to meet \n international standards."
            )
            desc_obj = c.beginText(50, 780)
            desc_obj.setFont("Helvetica-Bold", 12.6)
            for line in description_text.split("\n"):
                desc_obj.textLine(line)
            c.drawText(desc_obj)
            spec_text = (
                "Specifications:\n \n "
                "• Whole, dried\n"
                "• HS Code: 07132000\n"
                "• Product Name: Chickpeas\n"
                "• Size: 8 mm - 12 mm\n"
                "• Color: Beige / Light Brown\n"
                "• Moisture: Max 12%\n"
                "• Admixture: Max 0.5%\n"
                "• Foreign Matter: Max 0.5%"
            )
            spec_obj = c.beginText(350, 500)
            spec_obj.setFont("Helvetica-Bold", 17)
            for line in spec_text.split("\n"):
                spec_obj.textLine(line)
            c.drawText(spec_obj)

        if index == 6:
            c.setFont("Helvetica-Bold", 30)
            c.setFillColor(colors.darkred)
            c.drawString(50, 800, "Thank you!")

            thank_you_text = (
                "Thank you for choosing Codex Automation Key.\n \n "
                "• We're honored to have the opportunity to \n serve you.\n \n "
                "• At Codex Automation Key, we believe that \n true progress"
                " lies at the convergence of \n global trade and intelligent automation.\n \n"
                "• As a team of tech-driven professionals, \n we specialize in building"
                "reliable, cutting-edge \n solutions that power industries across borders.\n \n"
                "• Whether it's optimizing operations through \n automation software"
                "or streamlining complex \n import-export processes,our goal is to \n "
                "provide seamless, smart, and scalable services.\n  \n"
                "• Over the years, we have built a reputation \n for being a trusted partner—"
                "valued for \n our commitment to quality, integrity, \n and timely execution.\n \n"
                "• Innovation isn't just a buzzword for us; \n it's a daily practice.\n \n"
                "• Every solution we design is crafted \n to meet the unique challenges"
                "of modern \n businesses and the fast-paced international \n market.\n \n"
                "• As we continue to grow, we are thankful \n for clients and collaborators"
                "who share \n our vision. \n \n • Your trust is the foundation of everything \n  we do,"
                "and we look forward to achieving \n even greater milestones together. \n \n " 
                "• Behind every system we build is a \n relationship we value.\n \n "
                "• We envision a world where smart automation\n  bridges borders and transforms businesses.\n \n "
                "• Your partnership fuels our purpose."
            )

            text_obj = c.beginText(50, 750)
            text_obj.setFont("Helvetica-Bold", 12)
            text_obj.setFillColor(colors.black)
            for line in thank_you_text.split("\n"):
                text_obj.textLine(line)
            c.drawText(text_obj)

            c.setFont("Helvetica-Bold", 13)
            c.setFillColor(colors.white)
            c.drawString(350, 400, "techcodexautomation@gmail.com")
            c.drawString(350, 300, "docwise.codexautomationkey.com")
            c.drawString(350, 200, "123-456-7890")
            c.drawString(350, 100, "Crystal IT Park, Indore (M.P.)")

        c.showPage()

    c.save()
    return FileResponse(path=output_pdf, filename="company_catalog.pdf", media_type='application/pdf')

# ✅ New API: Generate a single product page dynamically
@app.post("/generate-product-page")
async def generate_product_page(
    name: str = Form(...),
    description: str = Form(...),
    specifications: str = Form(...)
):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"<b>Product Name:</b> {name}", styles["Title"]))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"<b>Description:</b><br/>{description.replace(chr(10), '<br/>')}", styles["BodyText"]))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"<b>Specifications:</b><br/>{specifications.replace(chr(10), '<br/>')}", styles["BodyText"]))
    doc.build(story)

    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=product_page.pdf"}
    )
