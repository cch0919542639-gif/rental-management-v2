from app.integrations.line_webhook import line_webhook_bp
from app.modules.auth import auth_bp
from app.modules.billing import billing_bp
from app.modules.contracts import contracts_bp
from app.modules.dashboard import dashboard_bp
from app.modules.electricity import electricity_bp
from app.modules.landlords import landlords_bp
from app.modules.maintenance import maintenance_bp
from app.modules.payments import payments_bp
from app.modules.properties import properties_bp
from app.modules.reports import reports_bp
from app.modules.rooms import rooms_bp
from app.modules.tenants import tenants_bp
from app.modules.water import water_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(contracts_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(electricity_bp)
    app.register_blueprint(landlords_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(properties_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(tenants_bp)
    app.register_blueprint(water_bp)
    app.register_blueprint(line_webhook_bp)
