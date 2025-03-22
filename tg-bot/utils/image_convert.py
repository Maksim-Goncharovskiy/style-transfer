from PIL import Image
from io import BytesIO


def image_to_bytes(img: Image.Image) -> bytes:
    byte_array = BytesIO()
    img.save(byte_array, format='jpeg')
    return byte_array.getvalue()


def bytes_to_image(data: bytes) -> Image.Image:
    byte_array = BytesIO(data)
    byte_array.seek(0)
    return Image.open(byte_array)

