import config
from pybit.unified_trading import HTTP

session = HTTP(
    testnet=False,
    api_key=config.API_KEY,
    api_secret=config.API_SECRET,
)

try:
    print("Probando conexion con Bybit...")
    res = session.get_closed_pnl(category="linear", limit=5)
    trades = res.get("result", {}).get("list", [])
    print(f"EXITO: Conectado. Se recuperaron {len(trades)} trades.")
    for t in trades:
        print(f"Par: {t['symbol']} | PnL: {t['closedPnl']} USDT")
except Exception as e:
    print(f"ERROR: {e}")