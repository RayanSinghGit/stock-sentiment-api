from flask import Flask
from flask_cors import CORS

from api.stock_bp import stock_bp
from api.ticker_lookup import ticker_lookup_bp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Register routes from modular files
app.register_blueprint(stock_bp)
app.register_blueprint(ticker_lookup_bp)

# Force CORS headers
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)

