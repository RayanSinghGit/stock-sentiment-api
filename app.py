from flask import Flask
from flask_cors import CORS
from api.stock_bp import stock_bp
from api.ticker_lookup import search_stocks  # <-- you don't need ticker_bp anymore

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Only register stock_bp, NOT ticker_bp
app.register_blueprint(stock_bp)

@app.route("/api/search_ticker")
def handle_search_ticker():
    from flask import request, jsonify
    query = request.args.get("query", "")
    results = search_stocks(query)
    return jsonify(results)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)

