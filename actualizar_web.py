import config
from pybit.unified_trading import HTTP
import MetaTrader5 as mt5
import json
from datetime import datetime

# 1. DEFINIR DÍA CERO (31 de Octubre de 2026)
fecha_inicio = datetime(2026, 10, 30)
start_time_ms = int(fecha_inicio.timestamp() * 1000)

print("Iniciando Motor Quant...")
todos_los_trades = []

# ==========================================
# 2. EXTRACCIÓN BYBIT (Contratos Perpetuos)
# ==========================================
session = HTTP(testnet=False, api_key=config.API_KEY, api_secret=config.API_SECRET)
try:
    print("Conectando a Bybit (API V5)...")
    res = session.get_closed_pnl(category="linear", limit=100, startTime=start_time_ms)
    trades_bybit = res.get("result", {}).get("list", [])
    
    for t in trades_bybit:
        todos_los_trades.append({
            "plataforma": "Bybit",
            "simbolo": t.get("symbol"),
            "pnl": float(t.get("closedPnl", 0)),
            "timestamp_ms": int(t.get("updatedTime", 0))
        })
    print(f"-> {len(trades_bybit)} trades recuperados de Bybit.")
except Exception as e:
    print(f"Error Bybit: {e}")

# ==========================================
# 3. EXTRACCIÓN METATRADER 5 (Índices/Forex)
# ==========================================
print("Conectando a MetaTrader 5...")
if mt5.initialize():
    autorizado = mt5.login(config.MT5_LOGIN, password=config.MT5_PASSWORD, server=config.MT5_SERVER)
    if autorizado:
        # Corregido: Fecha lejana en el futuro para evitar problemas de zona horaria
        deals = mt5.history_deals_get(fecha_inicio, datetime(2030, 1, 1)) 
        if deals:
            for deal in deals:
                # En MT5, deal.entry == 1 significa cerrar una posición
                if deal.entry == 1:
                    todos_los_trades.append({
                        "plataforma": "MT5",
                        "simbolo": deal.symbol,
                        "pnl": float(deal.profit),
                        "timestamp_ms": int(deal.time) * 1000 # MT5 usa segundos, pasamos a ms
                    })
            print(f"-> Trades recuperados de MT5 con éxito.")
    else:
        print(f"Error de login MT5. Verifica usuario, pass y servidor en config.py")
    mt5.shutdown()
else:
    print("Error: No se pudo inicializar MT5. ¿Está instalado el programa en tu PC?")

# ==========================================
# 4. ORDENAMIENTO CRONOLÓGICO Y CÁLCULOS
# ==========================================
# Orden estricto: del más viejo al más nuevo (para que el gráfico vaya de izq a der)
todos_los_trades.sort(key=lambda x: x["timestamp_ms"])

capital = 520 
balance = capital
ganadoras = 0
perdedoras = 0
g_profit = 0.0
g_loss = 0.0
curva = []

for t in todos_los_trades:
    pnl = t["pnl"]
    if pnl > 0:
        ganadoras += 1
        g_profit += pnl
    elif pnl < 0:
        perdedoras += 1
        g_loss += abs(pnl)
        
    balance += pnl
    crecimiento = ((balance - capital) / capital) * 100
    fecha_str = datetime.fromtimestamp(t["timestamp_ms"]/1000).strftime('%Y-%m-%d %H:%M')
    
    curva.append({
        "fecha": fecha_str,
        "simbolo": t["simbolo"],
        "origen": t["plataforma"],
        "crecimiento_pct": round(crecimiento, 2),
        "resultado": "WIN" if pnl > 0 else "LOSS"
    })

total = ganadoras + perdedoras
win_rate = (ganadoras / total * 100) if total > 0 else 0
profit_factor = (g_profit / g_loss) if g_loss > 0 else g_profit

datos_exportar = {
    "metricas": {
        "win_rate": round(win_rate, 2),
        "profit_factor": round(profit_factor, 2),
        "total_trades": total,
        "retorno_total_pct": round(((balance - capital) / capital) * 100, 2)
    },
    "curva": curva
}

with open("data.json", "w") as f:
    json.dump(datos_exportar, f, indent=4)

print("¡Track Record integrado guardado en data.json!")