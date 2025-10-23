import io
from pdf2image import convert_from_bytes
from PIL import Image


def pdf_to_image_bytes(pdf_bytes: bytes, dpi: int = 200) -> bytes:
    """
    Convert PDF bytes to image bytes (PNG format).
    If PDF has multiple pages, converts the first page.

    Args:
        pdf_bytes: PDF file as bytes
        dpi: Resolution for conversion (default 200)

    Returns:
        Image bytes in PNG format
    """
    try:
        # Convert PDF to list of PIL Images (one per page)
        images = convert_from_bytes(pdf_bytes, dpi=dpi)

        if not images:
            raise ValueError("PDF conversion resulted in no images")

        # Take the first page
        first_page = images[0]

        # Convert PIL Image to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='PNG', quality=95)
        img_byte_arr.seek(0)

        return img_byte_arr.getvalue()

    except Exception as e:
        raise ValueError(f"Failed to convert PDF to image: {str(e)}")


def is_pdf(file_bytes: bytes) -> bool:
    """
    Check if the file is a PDF by examining the file header.

    Args:
        file_bytes: File content as bytes

    Returns:
        True if file is PDF, False otherwise
    """
    return file_bytes.startswith(b'%PDF')


def convert_to_supported_format(image_bytes: bytes, target_format: str = "PNG") -> tuple[bytes, str]:
    """
    Convert image to a format supported by OpenAI (PNG, JPEG, GIF, WEBP).

    Args:
        image_bytes: Image file as bytes
        target_format: Target format (default PNG)

    Returns:
        Tuple of (converted image bytes, mime type)
    """
    try:
        # Open image with PIL
        img = Image.open(io.BytesIO(image_bytes))

        # Convert RGBA to RGB for JPEG
        if target_format.upper() == "JPEG" and img.mode == "RGBA":
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3] if len(
                img.split()) == 4 else None)
            img = rgb_img

        # Convert to target format
        output = io.BytesIO()
        img.save(output, format=target_format.upper())
        output.seek(0)

        # Map format to MIME type
        mime_types = {
            "PNG": "image/png",
            "JPEG": "image/jpeg",
            "JPG": "image/jpeg",
            "GIF": "image/gif",
            "WEBP": "image/webp"
        }

        mime_type = mime_types.get(target_format.upper(), "image/png")

        return output.getvalue(), mime_type

    except Exception as e:
        raise ValueError(f"Failed to convert image format: {str(e)}")


def get_image_format(image_bytes: bytes) -> str:
    """
    Detect the format of an image from its bytes.

    Args:
        image_bytes: Image file as bytes

    Returns:
        Image format as string (e.g., 'PNG', 'JPEG', 'GIF')
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        return img.format or "UNKNOWN"
    except Exception:
        return "UNKNOWN"
