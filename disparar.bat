@echo off
REM ============================================================
REM  Agente de Cotacoes - disparo completo local
REM  Grava a cotacao, gera os graficos e envia TUDO pro Telegram
REM  (token/chat_id vem das VARIAVEIS DE AMBIENTE do Windows)
REM  Config: Painel de Controle > Sistema > Variaveis de Ambiente
REM ============================================================
chcp 65001 >nul
cd /d C:\Users\Carlos\GitHub\agente-cotacoes

echo ============================================
echo  Agente de Cotacoes - iniciando...
echo ============================================
echo  [1/3] Gravando cotacao na planilha...
python agente_cotacoes.py

echo.
echo  [2/3] Gerando graficos de evolucao...
python gerar_graficos.py

echo.
echo  [3/3] Enviando tudo para o Telegram...
python enviar_telegram.py

echo.
echo ============================================
echo  Concluido!
echo   - Planilha: cotacoes_historico.xlsx
echo   - Graficos: graficos\*.png
echo   - Telegram: relatorio + graficos
echo ============================================
echo.
pause