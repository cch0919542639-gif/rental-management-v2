from flask import Blueprint, render_template
from flask_login import login_required

from app.services import MaintenanceService

maintenance_bp = Blueprint("maintenance", __name__, url_prefix="/maintenance")


@maintenance_bp.get("/")
@login_required
def maintenance_index():
    rooms = MaintenanceService.room_snapshot()
    return render_template("maintenance/index.html", rooms=rooms)
