import time
import websocket
import json
from typing import Dict, Callable, Optional


class BinanceTradesClient:
    """Client for Binance USD(S)-M Futures API."""
    
    WS_URL = "wss://fstream.binance.com/ws"
    
    def __init__(self, symbol: str = "BTCUSDT"):
        self.symbol = symbol
    
    def stream_trades(self, callback: Callable[[Dict], None], duration: float = 10):
        """
        Stream trades in real-time via WebSocket.
        
        Args:
            callback: Function to call for each trade
            duration: Duration in seconds
        """
        ws_endpoint = f"{self.WS_URL}/{self.symbol.lower()}@aggTrade"
        print(f"Connecting to: {ws_endpoint}")
        
        try:
            ws = websocket.create_connection(ws_endpoint)
            print(f"Streaming {self.symbol} trades...")
            
            start_time = time.time()
            while time.time() - start_time < duration:
                message = ws.recv()
                trade = json.loads(message)
                callback(trade)
            
            ws.close()
            print("WebSocket closed")
            
        except Exception as e:
            print(f"WebSocket error: {e}")
    
    def parse_trade(self, trade: Dict) -> Optional[Dict]:
        """
        Parse and validate trade structure.
        Time Complexity: O(1) - 7 constant field extractions
        Space Complexity: O(1) - Returns same dict or None
        
        Returns:
            Parsed trade dict if valid, None otherwise
        """
        try:
            # Validate all required fields exist and have correct types
            if not (
                isinstance(trade.get("a"), int) and
                isinstance(trade.get("p"), str) and
                isinstance(trade.get("q"), str) and
                isinstance(trade.get("f"), int) and
                isinstance(trade.get("l"), int) and
                isinstance(trade.get("T"), int) and
                isinstance(trade.get("m"), bool)
            ):
                return None
            
            # Return the parsed trade (already in correct format from JSON)
            return {
                "a": trade["a"],  # Aggregate tradeId
                "p": trade["p"],  # Price
                "q": trade["q"],  # Quantity
                "f": trade["f"],  # First tradeId
                "l": trade["l"],  # Last tradeId
                "T": trade["T"],  # Timestamp
                "m": trade["m"]   # Was buyer the maker?
            }
        except (KeyError, TypeError):
            return None
    
    def measure_parsing_speed(self, duration: float = 5) -> Dict:
        """Measure parsing performance on live stream."""
        trades = []
        
        def collect_trade(trade):
            trades.append(trade)
        
        print(f"Collecting trades for {duration} seconds...")
        stream_start = time.perf_counter()
        self.stream_trades(callback=collect_trade, duration=duration)
        stream_time = time.perf_counter() - stream_start
        
        if not trades:
            return {}
        
        # Measure parsing time
        parse_start = time.perf_counter()
        parsed_trades = [self.parse_trade(t) for t in trades]
        valid_count = sum(1 for t in parsed_trades if t is not None)
        parse_time = time.perf_counter() - parse_start
        
        count = len(trades)
        metrics = {
            "total_trades": count,
            "valid_trades": valid_count,
            "stream_time_sec": stream_time,
            "parse_time_ms": parse_time * 1000,
            "time_per_trade_ns": (parse_time * 1_000_000_000) / count,
            "parsing_throughput": count / parse_time,  # Validation speed
            "stream_throughput": count / stream_time   # Real-world speed
        }
        
        print(f"\n=== Parsing Performance ===")
        print(f"Total trades: {metrics['total_trades']}")
        print(f"Valid trades: {metrics['valid_trades']}")
        print(f"\nStream Performance:")
        print(f"  Duration: {metrics['stream_time_sec']:.2f}s")
        print(f"  Throughput: {metrics['stream_throughput']:.1f} trades/sec (network limited)")
        print(f"\nParsing Performance:")
        print(f"  Total time: {metrics['parse_time_ms']:.4f}ms")
        print(f"  Per trade: {metrics['time_per_trade_ns']:.2f}ns")
        print(f"  Throughput: {metrics['parsing_throughput']:.0f} trades/sec (CPU limited)")
        
        return metrics
    
    def print_trade(self, trade: Dict):
        """Print trade in assignment format."""
        print("[")
        print("  {")
        print(f'    "a": {trade["a"]},')
        print(f'    "p": "{trade["p"]}",')
        print(f'    "q": "{trade["q"]}",')
        print(f'    "f": {trade["f"]},')
        print(f'    "l": {trade["l"]},')
        print(f'    "T": {trade["T"]},')
        print(f'    "m": {str(trade["m"]).lower()}')
        print("  }")
        print("]")
