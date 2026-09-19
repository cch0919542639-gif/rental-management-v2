from pathlib import Path
from tempfile import TemporaryDirectory

from flask import Blueprint, current_app, flash, render_template
from flask_login import login_required
from werkzeug.utils import secure_filename

from app.integrations.ocr_client import create_ocr_client
from app.modules.utility_intake.forms import UtilityIntakeForm
from app.repositories import PropertyRepository

utility_intake_bp = Blueprint("utility_intake", __name__, url_prefix="/utility-intake")


def _populate_choices(form):
    form.property_id.choices = [(property_obj.id, property_obj.name) for property_obj in PropertyRepository.list_all()]


@utility_intake_bp.route("/", methods=["GET", "POST"])
@login_required
def intake():
    form = UtilityIntakeForm()
    _populate_choices(form)
    result = None
    if form.validate_on_submit():
        upload = form.document.data
        filename = secure_filename(upload.filename or "utility-document")
        max_size = current_app.config["OCR_MAX_UPLOAD_BYTES"]
        with TemporaryDirectory(prefix="rental-utility-ocr-") as temporary_dir:
            path = Path(temporary_dir) / filename
            upload.save(path)
            if path.stat().st_size > max_size:
                flash("上傳檔案超過大小限制，請縮小至 20 MB 以下。", "error")
            else:
                ocr = create_ocr_client().extract_text(str(path))
                result = {
                    "property_id": form.property_id.data,
                    "property_name": PropertyRepository.get_or_404(form.property_id.data).name,
                    "utility_type": form.utility_type.data,
                    "filename": filename,
                    "provider": ocr.provider,
                    "status": ocr.status,
                    "text": ocr.text or "",
                    "message": ocr.message,
                }
                return render_template("utility_intake/index.html", form=form, result=result)
    return render_template("utility_intake/index.html", form=form, result=result)
