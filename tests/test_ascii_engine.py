import io
from app.ascii_engine import text_to_ascii, image_to_ascii_text
from PIL import Image

def test_text_to_ascii():
    res = text_to_ascii("ok")
    assert isinstance(res, str)
    assert len(res) > 0

def test_image_to_ascii_text():
    # create tiny grayscale image
    img = Image.new("L", (20, 10), color=128)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b = buf.getvalue()
    out = image_to_ascii_text(b, width=10)
    assert isinstance(out, str)
    assert "\n" in out
