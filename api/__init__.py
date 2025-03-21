from flask import Blueprint

api_bp = Blueprint("api", __name__)

from . import stock_routes  # Ensure routes are registered

