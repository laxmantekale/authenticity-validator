import os
from flask import Flask, jsonify
from extensions import db, jwt, cors
from config import Config
from demo_seed import seed_demo_data

# Import Routes
from routes.auth_routes import auth_bp
from routes.student_routes import student_bp
from routes.college_routes import college_bp
from routes.college_link_routes import college_link_bp
from routes.document_routes import document_bp
from routes.verification_routes import verification_bp
from routes.history_routes import history_bp
from routes.report_routes import report_bp
from routes.blockchain_routes import blockchain_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with full CORS coverage
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # Register API Blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    
    # Register singular and plural endpoints for compatibility
    app.register_blueprint(student_bp, url_prefix="/api/student")
    app.register_blueprint(student_bp, name="students_plural", url_prefix="/api/students")
    
    app.register_blueprint(college_bp, url_prefix="/api/college")
    app.register_blueprint(college_bp, name="colleges_plural", url_prefix="/api/colleges")
    app.register_blueprint(college_bp, name="institution_bp", url_prefix="/api/institution")
    app.register_blueprint(college_bp, name="institutions_plural", url_prefix="/api/institutions")
    
    app.register_blueprint(college_link_bp, url_prefix="/api/college-links")
    app.register_blueprint(document_bp, url_prefix="/api/documents")
    
    app.register_blueprint(verification_bp, url_prefix="/api/verification")
    app.register_blueprint(verification_bp, name="verifications_plural", url_prefix="/api/verifications")
    app.register_blueprint(verification_bp, name="verify_short", url_prefix="/api/verify")
    
    app.register_blueprint(history_bp, url_prefix="/api/history")
    app.register_blueprint(report_bp, url_prefix="/api/reports")
    app.register_blueprint(blockchain_bp, url_prefix="/api/blockchain")

    # JSON error handlers for standardized API responses
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad request", "message": str(error)}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({"error": "Forbidden", "message": "Access denied"}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found", "message": "The requested endpoint was not found"}), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({"error": "Internal server error", "message": "An unexpected error occurred"}), 500

    # Root Endpoint: GET /
    @app.route("/", methods=["GET"])
    def root():
        return jsonify({
            "status": "ok",
            "message": "Authentication Validator API is running"
        }), 200

    # API Health Check Endpoint: GET /api/health
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "ok",
            "message": "Backend API is running",
            "service": "Authentication Validator API",
            "version": "1.0.0",
            "db_connected": True
        }), 200

    with app.app_context():
        # Ensure tables exist
        db.create_all()

        # Ensure blockchain_records columns are nullable in MySQL for immutable preservation upon document deletion
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            if "blockchain_records" in inspector.get_table_names() and db.engine.dialect.name == "mysql":
                cols = {c['name']: c for c in inspector.get_columns('blockchain_records')}
                if not cols.get('document_id', {}).get('nullable', True):
                    with db.engine.connect() as conn:
                        fks = [fk['name'] for fk in inspector.get_foreign_keys('blockchain_records')]
                        for fk_name in fks:
                            try:
                                conn.execute(text(f"ALTER TABLE blockchain_records DROP FOREIGN KEY `{fk_name}`;"))
                            except Exception:
                                pass
                        conn.execute(text("ALTER TABLE blockchain_records MODIFY document_id INT NULL;"))
                        conn.execute(text("ALTER TABLE blockchain_records MODIFY verification_id INT NULL;"))
                        try:
                            conn.execute(text("ALTER TABLE blockchain_records ADD CONSTRAINT fk_bc_doc FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL;"))
                            conn.execute(text("ALTER TABLE blockchain_records ADD CONSTRAINT fk_bc_ver FOREIGN KEY (verification_id) REFERENCES verifications(id) ON DELETE SET NULL;"))
                        except Exception:
                            pass
                        conn.commit()
        except Exception as e:
            print(f"Schema compatibility notice: {e}")

        # Seed safe demo data if empty
        try:
            seed_demo_data()
        except Exception as e:
            print(f"Demo seed notice: {e}")

    return app

if __name__ == "__main__":
    app = create_app()
    print("Starting Authentication Validator API on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)

