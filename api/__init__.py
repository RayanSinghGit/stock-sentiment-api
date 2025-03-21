from flask import Blueprint

api_bp = Blueprint("api", __name__)

# Import and register routes
from . import stock_routes, ticker_lookup

api_bp.register_blueprint(stock_routes.stock_bp)
api_bp.register_blueprint(ticker_lookup.ticker_bp)

