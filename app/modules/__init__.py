from app.modules.auth import auth_bp
from app.modules.billing import billing_bp
from app.modules.contracts import contracts_bp
from app.modules.dashboard import dashboard_bp
from app.modules.properties import properties_bp
from app.modules.rooms import rooms_bp
from app.modules.tenants import tenants_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(contracts_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(properties_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(tenants_bp)
