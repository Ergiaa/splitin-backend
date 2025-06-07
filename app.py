from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_restful import Api
from resources import init_resources
import settings

# ===================
# FLASK APP
# ===================
app = Flask(__name__)
CORS(app, origins=settings.CORS_ORIGINS)

# Firebase-based project: no SQLAlchemy setup
app.config['SECRET_KEY'] = settings.SECRET_KEY
app.config['BUNDLE_ERRORS'] = settings.BUNDLE_ERRORS
app.config['UPLOAD_FOLDER'] = settings.STATIC_DIRECTORY

# ===================
# RESTful API setup
# ===================
api = Api(app)

# ===================
# Error Handling
# ===================
from utils.response import abort

@app.errorhandler(Exception)
def handle_error(e):
    return abort("internal server error", 500, e)

# ===================
# Static Routes
# ===================
@app.route('/static/<path:path>', methods=['GET'])
def send_file(path):
    return send_from_directory('static', path)

# ===================
# API Endpoint Routes
# ===================
init_resources(api)

# ===================
# Entry Point
# ===================
if __name__ == '__main__':
    app.run(debug=True)