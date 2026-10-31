@echo off
echo ==============================================
echo MOTOR QUANT - THE PEAKY TRADING
echo ==============================================
echo Actualizando track record desde Bybit y MT5...
cd /d "C:\Users\maxim\Desktop\PYTHON TRACK RECORD"
"C:\Users\maxim\AppData\Local\Programs\Python\Python314\python.exe" actualizar_web.py
echo.
echo ¡Dashboard actualizado con exito!
pause