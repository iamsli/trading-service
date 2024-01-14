from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trades.db'
db = SQLAlchemy(app)

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    ticker = db.Column(db.String(10))
    side = db.Column(db.String(4))
    price = db.Column(db.Float)
    volume = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)
    status = db.Column(db.String(20))

@app.route('/submit_trade', methods=['POST'])
def submit_trade():
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['user_id', 'ticker', 'side', 'price', 'volume']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Validate numeric fields
        numeric_fields = ['price', 'volume']
        for field in numeric_fields:
            if not isinstance(data[field], (int, float)) or data[field] <= 0:
                return jsonify({'error': f'{field} must be a positive number'}), 400

        # Validate side
        valid_sides = ['buy', 'sell']
        if data['side'] not in valid_sides:
            return jsonify({'error': 'Invalid side. Must be "buy" or "sell"'}), 400

        new_trade = Trade(
            user_id=data['user_id'],
            ticker=data['ticker'],
            side=data['side'],
            price=data['price'],
            volume=data['volume'],
            timestamp=db.func.now(),
            status='pending'
        )
        
        # Add and commit the new trade to the database
        db.session.add(new_trade)
        db.session.commit()
        
        # Update trade status based on the success or failure of the database write
        # Change logic based on requirements
        try:
            db.session.flush()
            db.session.refresh(new_trade)

            new_trade.status = 'successful'
            db.session.commit()

            return jsonify({'message': 'Trade submitted successfully'}), 201

        except Exception as e:
            print(e) 
            new_trade.status = 'failed'
            db.session.commit()

            return jsonify({'error': 'Error writing to the database. Trade status set to "failed"'}), 500

    except Exception as e:
        print(e) 
        db.session.rollback()  # Rollback changes in case of an error
        return jsonify({'error': 'Internal Server Error accessing endpoint /submit_trade'}), 500

@app.route('/get_stats', methods=['GET'])
def get_stats():
    try:
        user_id = request.args.get('user_id')

        # Check if user_id is provided
        if not user_id:
            return jsonify({'error': 'Missing user_id parameter'}), 400

        # Retrieve trades from the database for the user
        trades = Trade.query.filter_by(user_id=user_id).all()

        # Check if trades are available for the user
        if not trades:
            return jsonify({'error': 'No trades found for the specified user'}), 404

        # Calculate per-ticker level stats
        ticker_stats = {}
        for trade in trades:
            ticker = trade.ticker
            if ticker not in ticker_stats:
                ticker_stats[ticker] = {
                    'highest_price': trade.price,
                    'lowest_price': trade.price,
                    'total_volume': trade.volume,
                    'total_value': trade.price * trade.volume
                }
            else:
                ticker_stats[ticker]['highest_price'] = max(ticker_stats[ticker]['highest_price'], trade.price)
                ticker_stats[ticker]['lowest_price'] = min(ticker_stats[ticker]['lowest_price'], trade.price)
                ticker_stats[ticker]['total_volume'] += trade.volume
                ticker_stats[ticker]['total_value'] += trade.price * trade.volume

        # Calculate VWAP for each ticker
        for ticker, stats in ticker_stats.items():
            stats['vwap'] = stats['total_value'] / stats['total_volume'] if stats['total_volume'] else 0

        return jsonify(ticker_stats)

    except Exception as e:
        print(e)  # Log the error for debugging
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/get_historical_trades', methods=['GET'])
def get_historical_trades():
    try:
        user_id = request.args.get('user_id')

        # Check if user_id is provided
        if not user_id:
            return jsonify({'error': 'Missing user_id parameter'}), 400

        trades = Trade.query.filter_by(user_id=user_id).all()

        # Check if trades are available for the user
        if not trades:
            return jsonify({'error': 'No historical trades found for the specified user'}), 404

        # Format trades into a list of dictionaries
        trade_list = [{
            'timestamp': trade.timestamp,
            'ticker': trade.ticker,
            'side': trade.side,
            'price': trade.price,
            'volume': trade.volume,
            'status': trade.status
        } for trade in trades]

        return jsonify({'historical_trades': trade_list})

    except Exception as e:
        print(e)
        return jsonify({'error': 'Internal Server Error accessing endpoint /get_historical_trades'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
