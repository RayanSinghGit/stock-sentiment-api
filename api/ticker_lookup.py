from flask import Blueprint, request, jsonify

ticker_bp = Blueprint("ticker", __name__)

# Example stock search function
@ticker_bp.route("/search_ticker", methods=["GET"])
def search_ticker():
    query = request.args.get("query", "").lower()

    if not query:
        return jsonify([])

    # Example static list
    stock_list = {
        "AAPL": "Apple Inc.",
        "GOOGL": "Alphabet Inc.",
        "TSLA": "Tesla Inc.",
        "TATAMOTORS.NS": "Tata Motors Ltd.",
        "RELIANCE.NS": "Reliance Industries Ltd.",
    }

    matches = [{"symbol": k, "name": v} for k, v in stock_list.items() if query in v.lower()]
    return jsonify(matches)

