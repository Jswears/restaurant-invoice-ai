from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.models.invoice_schema import InvoiceData
from app.services.openai_service import extract_invoice_data
from app.utils.image_utils import convert_to_supported_format, get_image_format, is_pdf, pdf_to_image_bytes

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.post("/extract", response_model=InvoiceData)
async def process_receipt(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()

        # Check if it's a PDF and convert if needed
        if is_pdf(image_bytes):
            image_bytes = pdf_to_image_bytes(image_bytes)
            content_type = "image/png"
        else:
            # Detect the actual image format
            img_format = get_image_format(image_bytes)

            # Supported formats by OpenAI
            supported_formats = ["PNG", "JPEG", "GIF", "WEBP"]

            if img_format not in supported_formats:
                # Convert to PNG if format is not supported
                image_bytes, content_type = convert_to_supported_format(
                    image_bytes, "PNG")
            else:
                # Use the detected format
                format_to_mime = {
                    "PNG": "image/png",
                    "JPEG": "image/jpeg",
                    "JPG": "image/jpeg",
                    "GIF": "image/gif",
                    "WEBP": "image/webp"
                }
                content_type = format_to_mime.get(img_format, "image/png")

        result = extract_invoice_data(image_bytes, content_type)

        # Explicitly return as JSONResponse to ensure proper JSON serialization
        return JSONResponse(
            content=result.model_dump(mode='json', exclude_none=False),
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
