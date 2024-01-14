## Getting started

### Setting up the service
**Install packages**
```
pip install -r requirements.txt
```

**Start the Flask service**
```
python3 trading_service.py
```

### Setting up the UI 
**Install dependencies**
```
git clone https://github.com/iamsli/trading-service-ui.git
cd trading-service-ui
npm install 
```
**Run the React app**
```npm start```

### Sample API calls
**Submit a trade**
```
curl -X POST -H "Content-Type: application/json" -d '{"user_id": "1", "ticker": "ORCL", "side": "buy", "price": 110.0, "volume": 100}' http://127.0.0.1:5000/submit_trade
```

**Get historical trades**
```
curl http://127.0.0.1:5000/get_historical_trades?user_id=1
```

**Get user stats**
```
curl http://127.0.0.1:5000/get_stats?user_id=1
```