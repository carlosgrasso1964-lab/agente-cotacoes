# -*- coding: utf-8 -*-
import requests
import datetime
import os
import sys
 
def debug(msg):
    agora = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{agora}] {msg}")
    sys.stdout.flush()
 
def get_cotacoes():
    dados = {
        'ibovespa': 'Consulte Home Broker',
        'dolar': 'Indisponivel',
        'euro': 'Indisponivel',
        'libra': 'Indisponivel',
        'ouro': 'Consulte mercado futuro',
        'bitcoin': 'Indisponivel'
    }
    headers = {'User-Agent': 'Mozilla/5.0'}
    debug("Buscando cotacoes...")
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        r = requests.get(url, headers=headers, timeout=20)
        debug(f"Cambio: {r.status_code}")
        if r.status_code == 200:
            rates = r.json().get('rates', {})
            usd = rates.get('BRL')
            eur = rates.get('EUR')
            gbp = rates.get('GBP')
            if usd:
                dados['dolar'] = f"R$ {usd:.2f}"
            if eur and usd:
                dados['euro'] = f"R$ {(usd/eur):.2f}"
            if gbp and usd:
                dados['libra'] = f"R$ {(usd/gbp):.2f}"
            debug(f"Dolar: {dados['dolar']}, Euro: {dados['euro']}, Libra: {dados['libra']}")
    except Exception as e:
        debug(f"Erro moedas: {e}")
    try:
        r = requests.get("https://api.coinbase.com/v2/prices/BTC-BRL/spot", headers=headers, timeout=15)
        debug(f"Bitcoin: {r.status_code}")
        if r.status_code == 200:
            btc = float(r.json()['data']['amount'])
            dados['bitcoin'] = f"R$ {btc:,.2f}"
            debug(f"BTC: {dados['bitcoin']}")
    except Exception as e:
        debug(f"Erro BTC: {e}")
    return dados
 
if __name__ == "__main__":
    debug("INICIANDO RELATORIO")
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    cot = get_cotacoes()
    relatorio = f"""📊 Relatorio Diario - {hoje}
 
COTACOES:
- Dolar: {cot['dolar']}
- Euro: {cot['euro']}
- Libra: {cot['libra']}
- Bitcoin: {cot['bitcoin']}
- Ibovespa: {cot['ibovespa']}
- Ouro: {cot['ouro']}
 
Atualizado automaticamente."""
    print(relatorio)
    
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if token:
        debug(f"TOKEN encontrado")
    else:
        debug("TOKEN NAO ENCONTRADO!")
    if chat_id:
        debug(f"CHAT_ID encontrado: {chat_id}")
    else:
        debug("CHAT_ID NAO ENCONTRADO!")
    
    if token and chat_id:
        try:
            r = requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": relatorio, "parse_mode": "HTML"},
                timeout=15
            )
            debug(f"Telegram: {r.status_code}")
            if r.status_code == 200:
                debug("ENVIADO COM SUCESSO!")
            else:
                debug(f"Erro: {r.text[:200]}")
        except Exception as e:
            debug(f"Falha: {e}")
    else:
        debug("Variaveis de ambiente nao configuradas")
    debug("FIM")
