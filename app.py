import io, os, uuid, numpy as np, fitz
from flask import Flask, render_template, request, send_file, abort, make_response
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

def _has_structural_content(page):
    if page.first_annot:
        return True
    if page.get_links():
        return True
    if page.get_text("words"):
        return True
    if page.get_images(full=True):
        return True
    for d in page.get_drawings():
        stroke = d.get("color") or (1, 1, 1)
        fill = d.get("fill") or (1, 1, 1)
        if any(c < 0.995 for c in stroke) or any(c < 0.995 for c in fill):
            return True
    return False

def _raster_looks_blank(page, dpi_scale=2.0, gray_thresh=252, max_dark_ratio=0.0008, ignore_margin_px=6):
    m = fitz.Matrix(dpi_scale, dpi_scale)
    pm = page.get_pixmap(matrix=m, colorspace=fitz.csGRAY, alpha=False)
    h, w = pm.height, pm.width
    arr = np.frombuffer(pm.samples, dtype=np.uint8).reshape(h, w)
    if ignore_margin_px > 0 and h > 2*ignore_margin_px and w > 2*ignore_margin_px:
        arr = arr[ignore_margin_px:-ignore_margin_px, ignore_margin_px:-ignore_margin_px]
    total = arr.size
    dark = np.count_nonzero(arr < gray_thresh)
    return (dark / max(total, 1)) <= max_dark_ratio

def is_blank_page(page):
    if _has_structural_content(page):
        return False
    return _raster_looks_blank(page)

def strip_white_pages(pdf_bytes):
    src = fitz.open(stream=pdf_bytes, filetype="pdf")
    dst = fitz.open()
    for i in range(src.page_count):
        p = src.load_page(i)
        if not is_blank_page(p):
            dst.insert_pdf(src, from_page=i, to_page=i)
    out = b"" if dst.page_count == 0 else dst.tobytes()
    src.close()
    dst.close()
    return out

@app.errorhandler(RequestEntityTooLarge)
def too_large(e):
    return make_response(render_template("error.html", title="File too large", message="The PDF exceeds 100 MB."), 413)

@app.errorhandler(400)
def bad_request(e):
    msg = getattr(e, "description", "The server could not understand your request.")
    return make_response(render_template("error.html", title="Bad Request", message=msg), 400)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    f = request.files.get("file")
    if not f or f.filename.strip() == "":
        abort(400, description="No file received. Choose a PDF and try again.")
    data = f.read()
    if not data:
        abort(400, description="Uploaded file is empty.")
    try:
        cleaned = strip_white_pages(data)
    except fitz.FileDataError:
        abort(400, description="This PDF seems encrypted or invalid. Upload an unlocked/valid PDF.")
    except Exception:
        abort(400, description="Failed to process PDF.")
    if not cleaned:
        cleaned = data
    filename = os.path.splitext(f.filename or f"cleaned-" + uuid.uuid4().hex + ".pdf")[0] + "-cleaned.pdf"
    return send_file(io.BytesIO(cleaned), as_attachment=True, download_name=filename, mimetype="application/pdf")

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")), debug=False)
