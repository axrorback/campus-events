from flask import Flask, request, redirect, url_for, render_template_string
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
from io import BytesIO
import base64
import re

app = Flask(__name__)

ERR_MAP = {
    "L": ERROR_CORRECT_L,
    "M": ERROR_CORRECT_M,
    "Q": ERROR_CORRECT_Q,
    "H": ERROR_CORRECT_H,
}

def make_qr_base64(data: str, err_level: str = "M", box_size: int = 10, border: int = 4) -> str:
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERR_MAP.get(err_level, ERROR_CORRECT_M),
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def is_url(text: str) -> bool:
    url_regex = re.compile(
        r"^(https?://|www\.)[\w\-]+(\.[\w\-]+)+[/#?]?.*$", re.IGNORECASE
    )
    return bool(url_regex.match(text.strip()))

BASE_LAYOUT = """
<!doctype html>
<html lang="uz">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{ title or "QR generator & skaner" }}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { background: #0b1220; color: #e9eef7; }
    .card { background: #111a2b; border: 1px solid #1e2a44; }
    .form-control, .form-select { background:#0f1726; color:#e9eef7; border-color:#25334f; }
    .btn-primary { background:#2563eb; border-color:#1d4ed8; }
    .btn-outline-light { border-color:#3a4a6a; color:#e9eef7; }
    a { color:#93c5fd; text-decoration: none; }
    a:hover { color:#bfdbfe; }
    .qr-box img { max-width: 100%; height: auto; }
    .muted { color:#93a4c0; }
    .nav-pills .nav-link.active { background:#1e3a8a; }
    .footer { color:#6b7b99; font-size: 0.9rem; }
  </style>
</head>
<body>
<nav class="navbar navbar-expand-lg" style="background:#0f1726;border-bottom:1px solid #1e2a44;">
  <div class="container">
    <a class="navbar-brand text-light fw-bold" href="{{ url_for('index') }}">QR App</a>
    <ul class="navbar-nav ms-auto nav-pills">
      <li class="nav-item">
        <a class="nav-link {% if tab=='gen' %}active{% endif %}" href="{{ url_for('index') }}">QR yaratish</a>
      </li>
      <li class="nav-item">
        <a class="nav-link {% if tab=='scan' %}active{% endif %}" href="{{ url_for('scan') }}">QR skan qilish</a>
      </li>
    </ul>
  </div>
</nav>

<main class="container py-4">
  {% block content %}{% endblock %}
</main>

<footer class="container pb-4 footer">
  <div class="d-flex justify-content-between">
    <span>Made with Flask · html5-qrcode</span>
    <span>⚡ Offline serverda QR generatsiya, brauzerda skan</span>
  </div>
</footer>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

INDEX_TPL = """
{% extends base %}
{% block content %}
<div class="row g-4">
  <div class="col-lg-7">
    <div class="card p-4">
      <h3 class="mb-3">Matn yoki link kiriting → QR</h3>
      <form method="post" action="{{ url_for('index') }}" class="vstack gap-3">
        <div>
          <label class="form-label">Matn / URL</label>
          <textarea class="form-control" name="data" rows="4" placeholder="Masalan: https://example.com yoki 'Assalomu alaykum'" required>{{ form_data.get('data','') }}</textarea>
          <div class="form-text muted">* Link bo‘lsa, natijada ochish tugmasi ham chiqadi.</div>
        </div>

        <div class="row g-3">
          <div class="col-md-4">
            <label class="form-label">Xatolik darajasi</label>
            <select class="form-select" name="err">
              {% for e in ["L","M","Q","H"] %}
                <option value="{{e}}" {% if form_data.get('err','M')==e %}selected{% endif %}>{{e}}</option>
              {% endfor %}
            </select>
            <div class="form-text muted">L (eng yengil) → H (eng kuchli)</div>
          </div>
          <div class="col-md-4">
            <label class="form-label">Box size</label>
            <input type="number" min="4" max="20" class="form-control" name="box" value="{{ form_data.get('box',10) }}">
          </div>
          <div class="col-md-4">
            <label class="form-label">Border</label>
            <input type="number" min="1" max="10" class="form-control" name="border" value="{{ form_data.get('border',4) }}">
          </div>
        </div>

        <div class="d-flex gap-2">
          <button class="btn btn-primary" type="submit">QR yaratish</button>
          <a class="btn btn-outline-light" href="{{ url_for('index') }}">Tozalash</a>
        </div>
      </form>
    </div>
  </div>

  <div class="col-lg-5">
    <div class="card p-4">
      <h4 class="mb-3">Natija</h4>
      {% if qr_b64 %}
        <div class="qr-box text-center mb-3">
          <img id="qrImg" src="data:image/png;base64,{{ qr_b64 }}" alt="QR code" class="img-fluid rounded border">
        </div>
        <div class="vstack gap-2">
          <a class="btn btn-primary" id="btnDownload" download="qr.png" href="data:image/png;base64,{{ qr_b64 }}">Yuklab olish (.png)</a>
          <button class="btn btn-outline-light" id="btnCopy">Matnni nusxalash</button>
          {% if is_link %}
            <a class="btn btn-outline-light" target="_blank" rel="noopener" href="{{ safe_link }}">Havolani ochish</a>
          {% endif %}
        </div>
        <div class="mt-3">
          <div class="form-text muted">Manba matn:</div>
          <pre class="p-3 rounded" style="background:#0f1726; white-space: pre-wrap;">{{ text }}</pre>
        </div>
      {% else %}
        <p class="muted">Chap tomonda matn/link kiriting va “QR yaratish” tugmasini bosing.</p>
      {% endif %}
    </div>
  </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', () => {
  const btnCopy = document.getElementById('btnCopy');
  if (btnCopy) {
    btnCopy.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText({{ text|tojson }});
        btnCopy.innerText = "Nusxalandi ✓";
        setTimeout(() => btnCopy.innerText = "Matnni nusxalash", 1500);
      } catch(e) { alert("Clipboard ishlamadi: " + e); }
    });
  }
});
</script>
{% endblock %}
"""

SCAN_TPL = """
{% extends base %}
{% block content %}
<div class="row">
  <div class="col-lg-8">
    <div class="card p-4">
      <h3 class="mb-3">Kamera orqali skan</h3>
      <div id="reader" class="rounded border" style="overflow:hidden;"></div>
      <div class="mt-3">
        <button id="btnStart" class="btn btn-primary me-2">Skannerni ishga tushirish</button>
        <button id="btnStop" class="btn btn-outline-light">To‘xtatish</button>
      </div>
      <div class="mt-3 muted">* Agar kamera ruxsat so‘rasa — “Allow/Permissiya” bering.</div>
    </div>
  </div>
  <div class="col-lg-4">
    <div class="card p-4">
      <h4 class="mb-3">Rasm faylidan skan</h4>
      <input class="form-control" type="file" id="fileInp" accept="image/*">
      <div class="form-text muted mt-2">PNG/JPG rasm yuklab, ichidagi QR’ni o‘qish mumkin.</div>
    </div>

    <div class="card p-4 mt-3">
      <h4 class="mb-3">Natija</h4>
      <div id="resultBox" class="vstack gap-2">
        <div class="muted">Hozircha natija yo‘q.</div>
      </div>
    </div>
  </div>
</div>

<!-- html5-qrcode CDN -->
<script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
<script>
let html5Qrcode, isRunning = false;

function showResult(text) {
  const box = document.getElementById('resultBox');
  box.innerHTML = "";
  const pre = document.createElement('pre');
  pre.className = "p-3 rounded";
  pre.style.background = "#0f1726";
  pre.style.whiteSpace = "pre-wrap";
  pre.textContent = text;
  box.appendChild(pre);

  try {
    const u = new URL(text);
    const a = document.createElement('a');
    a.href = u.href;
    a.target = "_blank";
    a.rel = "noopener";
    a.className = "btn btn-primary mt-2";
    a.textContent = "Havolani ochish";
    box.appendChild(a);
  } catch(_) {
    // matn URL bo'lmasa, tugma chiqarmaymiz
  }
}

async function startScanner() {
  if (isRunning) return;
  const el = document.getElementById('reader');
  html5Qrcode = new Html5Qrcode(/* element id */ "reader");
  const config = { fps: 10, qrbox: 250, aspectRatio: 1.777 }; // default sozlamalar
  try {
    isRunning = true;
    await html5Qrcode.start(
      { facingMode: "environment" },
      config,
      (decodedText) => {
        showResult(decodedText);
      }
    );
  } catch (e) {
    isRunning = false;
    alert("Skanner ishga tushmadi: " + e);
  }
}

async function stopScanner() {
  if (!html5Qrcode || !isRunning) return;
  await html5Qrcode.stop();
  await html5Qrcode.clear();
  isRunning = false;
}

document.getElementById('btnStart').addEventListener('click', startScanner);
document.getElementById('btnStop').addEventListener('click', stopScanner);

document.getElementById('fileInp').addEventListener('change', async (e) => {
  const file = e.target.files?.[0];
  if (!file) return;
  try {
    const result = await Html5QrcodeScanner.scanFile(file, true);
    showResult(result);
  } catch (err) {
    alert("O‘qib bo‘lmadi: " + err);
  }
});
</script>
{% endblock %}
"""

@app.route("/", methods=["GET", "POST"])
def index():
    qr_b64 = None
    text = ""
    is_link = False
    safe_link = ""
    form_defaults = {"err":"M", "box":10, "border":4}

    if request.method == "POST":
        text = (request.form.get("data") or "").strip()
        err = (request.form.get("err") or "M").upper()
        box = int(request.form.get("box") or 10)
        border = int(request.form.get("border") or 4)

        if text:
            qr_b64 = make_qr_base64(text, err, box, border)
            is_link = is_url(text)
            safe_link = text if text.startswith(("http://","https://")) else f"https://{text}" if text.startswith("www.") else text
        form_defaults = {"err":err, "box":box, "border":border}

    return render_template_string(
        INDEX_TPL,
        base=BASE_LAYOUT,
        title="QR yaratish",
        tab="gen",
        qr_b64=qr_b64,
        text=text,
        is_link=is_link,
        safe_link=safe_link,
        form_data=form_defaults
    )

@app.route("/scan")
def scan():
    return render_template_string(
        SCAN_TPL,
        base=BASE_LAYOUT,
        title="QR skan qilish",
        tab="scan"
    )

if __name__ == "__main__":
    app.run(debug=True)
