"""
vasAI API Server — port 6000
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

load_dotenv(Path(__file__).parent.parent / ".env")


def create_app() -> Flask:
    app = Flask(__name__)

    from api.routes.health import bp as health_bp
    from api.routes.events import bp as events_bp
    from api.routes.audit import bp as audit_bp
    from api.routes.caliber_routes import bp as caliber_bp
    from api.routes.governance_routes import bp as governance_bp
    from api.routes.shadow_routes import bp as shadow_bp
    from api.routes.evidence_routes import bp as evidence_bp
    from api.routes.phi_routes import bp as phi_bp
    from api.routes.phios_routes import bp as phios_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(caliber_bp)
    app.register_blueprint(governance_bp)
    app.register_blueprint(shadow_bp)
    app.register_blueprint(evidence_bp)
    app.register_blueprint(phi_bp)
    app.register_blueprint(phios_bp)

    from api.state import init_app_state
    with app.app_context():
        init_app_state()

    return app


if __name__ == "__main__":
    port = int(os.environ.get("VASAI_PORT", 6000))
    app = create_app()
    print(f"vasAI COMMAND CENTER starting on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
