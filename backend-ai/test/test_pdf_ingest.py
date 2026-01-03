import asyncio
import httpx
from reportlab.pdfgen import canvas
from pathlib import Path
import os

async def test_pdf_ingest():
    # 1. Create a dummy PDF
    pdf_path = Path("test_doc.pdf")
    c = canvas.Canvas(str(pdf_path))
    c.drawString(100, 750, "Greeting from the test script!")
    c.drawString(100, 730, "This is a test PDF document for ingestion.")
    c.drawString(100, 710, "It contains some simple text to be extracted.")
    c.save()
    
    print(f"Created temporary PDF at {pdf_path.absolute()}")

    try:
        # 2. Upload to API
        url = "http://localhost:8000/api/v1/ingest"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            with open(pdf_path, "rb") as f:
                files = {"files": ("test_doc.pdf", f, "application/pdf")}
                print(f"Uploading to {url}...")
                response = await client.post(url, files=files)
                
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n--- Success ---")
            print(f"Doc ID: {data.get('doc_id')}")
            print(f"Status: {data.get('status')}")
            print(f"Filename: {data.get('filename')}")
        else:
            print("\n--- Failed ---")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        if pdf_path.exists():
            pdf_path.unlink()
            print("Cleaned up temporary file.")

if __name__ == "__main__":
    asyncio.run(test_pdf_ingest())
