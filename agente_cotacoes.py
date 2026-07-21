# -*- coding: utf-8 -*-
import requests
import datetime
import os
 
def get_cotacoes():
    dados = {
        'ibovespa': 'Indisponivel',
        'dolar': 'Indisponivel',
        'euro': 'Indisponivel',
        'libra': 'Indisponivel',
        'ouro': 'Indisponivel',
        'bitcoin': 'Indisponivel'
    }
    h = {'User-Agent': 'Mozilla/5.0'}
    
    # Moedas e Bitcoin
    try:
        r = requests.get("https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,GBP-BRL,BTC-BRL", headers=h, timeout=15)
        if r.status_code == 200:
            d = r.json()
            dados['dolar'] = f"R$ {float(d['USDBRL']['bid']):.2f}"
            dados['euro'] = f"R$ {float(d['EURBRL']['bid']):.2f}"
            dados['libra'] = f"R$ {float(d['GBPBRL']['bid']):.2f}"
            dados['bitcoin'] = f"R$ {float(d['BTCBRL']['bid']):,.2f}"
            dados['usd'] = float(d['USDBRL']['bid'])
    except: pass
    
    # Ibovespa
    try:
        r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/%5EBVSP?interval=1d&range=1d", headers=h, timeout=15)
        if r.status_code == 200:
            dados['ibovespa'] = f"{r.json()['chart']['result'][0]['meta']['regularMarketPrice']:,.2f} pts"
    except: pass
    
    # Ouro
    try:
        r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/GC%3DF?interval=1d&range=1d", headers=h, timeout=15)
        if r.status_code == 200:
            gold = r.json()['chart']['result'][0]['meta']['regularMarketPrice']
            usd = dados.get('usd', 5.0)
            dados['ouro'] = f"R$ {(gold * usd):,.2f}/oz"
    except: pass
    
    return dados
 
if __name__ == "__main__":
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    cot = get_cotacoes()
    
    relatorio = f"""📊 Relatorio Diario - {hoje}
 
COTACOES:
- Ibovespa: {cot['ibovespa']}
- Dolar: {cot['dolar']}
- Euro: {cot['euro']}
- Libra: {cot['libra']}
- Ouro: {cot['ouro']}
- Bitcoin: {cot['bitcoin']}
 
Atualizado automaticamente."""
    
    print(relatorio)
    
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat_id:
        try:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": relatorio, "parse_mode": "HTML"}, timeout=15)
            print("Enviado para Telegram!")
        except Exception as e:
            print(f"Erro: {e}")
