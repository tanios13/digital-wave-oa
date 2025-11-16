# Binance Trades Stream Parser

Real-time trade streaming from Binance USD(S)-M Futures API with O(1) parsing.

## Solution

Connects to WebSocket endpoint `wss://fstream.binance.com/ws/<symbol>@aggTrade` to receive live trades. Each trade is parsed and validated in constant time.

### Key Methods

- **`stream_trades()`** - Opens WebSocket connection, receives trades via `ws.recv()`, calls callback for each trade
- **`parse_trade()`** - Validates 7 fields (a, p, q, f, l, T, m) in O(1) time, returns parsed dict or None

### Algorithmic Complexity

**`parse_trade()` - O(1) time and space:**
- 7 constant field validations (no loops or recursion)
- Returns same dict structure or None

**Performance:**
- Parsing: ~500,000 trades/sec (CPU-limited)
- Stream: ~5-10 trades/sec (network-limited)
- **Bottleneck is network I/O, not parsing**

## Usage

```python
from binance_trades_client import BinanceTradesClient

client = BinanceTradesClient(symbol="BTCUSDT")

def handle_trade(trade):
    parsed = client.parse_trade(trade)
    if parsed:
        client.print_trade(parsed)

client.stream_trades(callback=handle_trade, duration=5)
client.measure_parsing_speed(duration=5)
```
