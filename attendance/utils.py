import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from pathlib import Path

def generate_qr_png(data: str) -> bytes:
    qr = qrcode.QRCode(version=2, box_size=8, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def build_invitation(
    user_fullname: str,
    email: str,
    event_title: str,
    when_str: str,
    where_str: str,
    room_str: str,
    user_photo_path: str,
    qr_png_bytes: bytes,
    qr_text: str = ""
) -> bytes:
    # Canvas
    W, H = 1200, 800
    bg = Image.new('RGB', (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(bg)

    # Fonts
    font_big = ImageFont.load_default()
    font_med = ImageFont.load_default()
    font_small = ImageFont.load_default()

    # Header banner
    header_h = 140
    draw.rectangle([(0,0),(W,header_h)], fill=(25, 118, 210))  # ko‘k banner
    draw.text((40, 50), "🎫 Event Invitation", fill=(255,255,255), font=font_big)

    # User photo
    x_photo, y_photo = 60, header_h + 40
    try:
        photo = Image.open(user_photo_path).convert("RGB")
        photo = photo.resize((200, 200))
        bg.paste(photo, (x_photo, y_photo))
    except Exception:
        draw.rectangle([(x_photo, y_photo), (x_photo+200, y_photo+200)], fill=(230,230,230))
        draw.text((x_photo+50, y_photo+90), "No Photo", fill=(120,120,120), font=font_small)

    # User info
    text_x = x_photo + 240
    draw.text((text_x, y_photo), f"👤 {user_fullname}", fill=(0,0,0), font=font_big)
    draw.text((text_x, y_photo+40), f"📧 {email or '-'}", fill=(50,50,50), font=font_med)
    draw.text((text_x, y_photo+90), f"📌 Event: {event_title}", fill=(0,0,0), font=font_med)
    draw.text((text_x, y_photo+140), f"🕒 {when_str}", fill=(0,0,0), font=font_med)
    draw.text((text_x, y_photo+190), f"📍 {where_str}", fill=(0,0,0), font=font_med)
    if room_str:
        draw.text((text_x, y_photo+240), f"🏫 Room: {room_str}", fill=(0,0,0), font=font_med)

    # QR code
    qr = Image.open(BytesIO(qr_png_bytes))
    qr = qr.resize((280, 280))
    qr_x, qr_y = W - 360, y_photo
    bg.paste(qr, (qr_x, qr_y))

    # QR payload text (optional)
    if qr_text:
        draw.text((qr_x, qr_y+300), qr_text, fill=(80,80,80), font=font_small)

    # Footer
    footer_text = "❗ Show this invitation at entry. The QR code is unique to you."
    draw.text((40, H-60), footer_text, fill=(90,90,90), font=font_small)

    # Save to bytes
    out = BytesIO()
    bg.save(out, format='PNG')
    return out.getvalue()


