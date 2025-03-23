from flask import Flask
from flask_cors import CORS
from api.ticker_lookup import ticker_bp
from api.stock_routes import stock_bp

app = Flask(__name__)

# ✅ Enable CORS globally
CORS(app)

# ✅ Register both blueprints
app.register_blueprint(ticker_bp)
app.register_blueprint(stock_bp)

if __name__ == '__main__':
    app.run(debug=True, port=10000)

