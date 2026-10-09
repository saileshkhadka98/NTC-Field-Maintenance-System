import uuid
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageOps
from rest_framework.exceptions import ValidationError

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
ALLOWED_FORMATS = {'JPEG', 'PNG', 'WEBP'}
FULL_SIZE = (1600, 1600)
THUMB_SIZE = (400, 400)


def validate_upload(uploaded):
    """Reject files that are too big or are not JPG/PNG/WebP images."""
    if uploaded.size > MAX_UPLOAD_BYTES:
        raise ValidationError('Image must be 5 MB or smaller.')
    try:
        with Image.open(uploaded) as img:
            image_format = img.format
    except Exception:
        raise ValidationError('Upload a valid image file.')
    finally:
        uploaded.seek(0)
    if image_format not in ALLOWED_FORMATS:
        raise ValidationError('Only JPG, PNG or WebP images are allowed.')
    return uploaded


def _encode(img, size):
    copy = img.copy()
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    buffer = BytesIO()
    copy.save(buffer, format='JPEG', quality=85, optimize=True)
    return buffer.getvalue()


def process_image(file_obj):
    """Return (full_size, thumbnail) JPEG files with random names.

    The re-encode also strips EXIF data (such as the phone's GPS position)
    and applies the camera rotation.
    """
    file_obj.seek(0)
    with Image.open(file_obj) as source:
        img = ImageOps.exif_transpose(source).convert('RGB')
    name = f'{uuid.uuid4().hex}.jpg'
    return (
        ContentFile(_encode(img, FULL_SIZE), name=name),
        ContentFile(_encode(img, THUMB_SIZE), name=name),
    )