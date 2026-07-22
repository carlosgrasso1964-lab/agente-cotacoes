# -*- coding: utf-8 -*-
import requests
import datetime
import os
import xml.etree.ElementTree as ET
 
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
    
    # USD/BRL
    try:
        r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/BRL%3DX?interval=1d&range=1d", headers=h, timeout=15)
        if r.status_code == 200:
            usd = r.json()['chart']['result'][0]['meta']['regularMarketPrice']
            dados['dolar'] = f"R$ {usd:.2f}"
            dados['usd'] = usd
    except: pass
    
    # EUR/BRL
    try:
        r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/EURBRL%3DX?interval=1d&range=1d", headers=h, timeout=15)
        if r.status_code == 200:
            eur = r.json()['chart']['result'][0]['meta']['regularMarketPrice']
            dados['euro'] = f"R$ {eur:.2f}"
    except: pass
    
    # GBP/BRL
    try:
        r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/GBPBRL%3DX?interval=1d&range=1d", headers=h, timeout=15)
        if r.status_code == 200:
            gbp = r.json()['chart']['result'][0]['meta']['regularMarketPrice']
            dados['libra'] = f"R$ {gbp:.2f}"
    except: pass
    
    # Bitcoin
    try:
        r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD?interval=1d&range=1d", headers=h, timeout=15)
        if r.status_code == 200:
            btc = r.json()['chart']['result'][0]['meta']['regularMarketPrice']
            usd = dados.get('usd', 5.0)
            dados['bitcoin'] = f"R$ {(btc * usd):,.2f}"
    except: pass
    
    # Ibovespa
    try:
        r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/%5EBVSP?interval=1d&range=1d", headers=h, timeout=15)
        if r.status_code == 200:
            ibov = r.json()['chart']['result'][0]['meta']['regularMarketPrice']
            dados['ibovespa'] = f"{ibov:,.2f} pts"
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
 
def buscar_rss(url, limite=3):
    """Busca noticias de um feed RSS e retorna lista de titulos com links"""
    noticias = []
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            for item in root.findall('.//item')[:limite]:
                titulo = item.findtext('title', '')
                link = item.findtext('link', '')
                if titulo:
                    noticias.append(f"- <a href='{link}'>{titulo[:100]}</a>")
    except: pass
    return noticias
 
def get_noticias():
    """Busca noticias do G1 e CNN Brasil"""
    noticias = []
    
    # G1 - principais noticias do Brasil
    noticias += buscar_rss("https://g1.globo.com/rss/g1/", 2)
    
    # CNN Brasil
    noticias += buscar_rss("https://www.cnnbrasil.com.br/feed/", 2)

    # Cruzeiro do Sul
    noticias += buscar_rss("https://www.jornalcruzeiro.com.br/", 2)
    
    if not noticias:
        noticias = ["- Nao foi possivel carregar as noticias."]
    
    return noticias
 
if __name__ == "__main__":
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    cot = get_cotacoes()
    noticias = get_noticias()
    
    relatorio = f"""📊 <b>Relatorio Diario - {hoje}</b>
 
<b>COTACOES:</b>
- Ibovespa: {cot['ibovespa']}
- Dolar: {cot['dolar']}
- Euro: {cot['euro']}
- Libra: {cot['libra']}
- Ouro: {cot['ouro']}
- Bitcoin: {cot['bitcoin']}
 
<b>NOTICIAS DO DIA:</b>
{chr(10).join(noticias)}
 
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
