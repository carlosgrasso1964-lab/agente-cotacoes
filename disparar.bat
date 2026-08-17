@echo off
REM ============================================================
REM  Agente de Cotacoes - modo local
REM  Grava a cotacao do dia na planilha e gera os graficos
REM  de evolucao. (Sem envio ao Telegram por enquanto.)
REM ============================================================
chcp 65001 >nul
cd /d C:\Users\Carlos\agente-cotacoes

echo ============================================
echo  Agente de Cotacoes - iniciando...
echo ============================================
echo.

echo [1/2] Gravando cotacao do dia na planilha...
python agente_cotacoes.py

echo.
echo [2/2] Gerando graficos de evolucao...
python gerar_graficos.py

echo.
echo ============================================
echo  Concluido!
echo  - Planilha:   cotacoes_historico.xlsx
echo  - Graficos:   graficos\*.png
echo ============================================
echo.
pause