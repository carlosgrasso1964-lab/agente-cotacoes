# -*- coding: utf-8 -*-
import requests
import datetime
import os
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

def get_cotacoes():
    dados = {
        'ibovespa': 'Indisponivel',
        'dolar': 'Indisponivel',
        'euro': 'Indisponivel',
        'libra': 'Indisponivel',
        'ouro': 'Indisponivel',
        'bitcoin': 'Indisponivel'
    }
    h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
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
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}, timeout=15)
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            for item in root.findall('.//item')[:limite]:
                titulo = item.findtext('title', '').strip()
                link = item.findtext('link', '').strip()
                if titulo:
                    noticias.append(f"- <a href='{link}'>{titulo[:100]}</a>")
    except Exception as e:
        print(f"Erro ao buscar RSS ({url}): {e}")
    return noticias

def get_noticias():
    """Busca noticias do G1 Nacional e CNN Brasil"""
    noticias = []
    noticias += buscar_rss("https://g1.globo.com/rss/g1/", 2)
    noticias += buscar_rss("https://www.cnnbrasil.com.br/feed/", 2)

    if not noticias:
        noticias = ["- Nao foi possivel carregar as noticias."]
    
    return noticias

def get_manchetes_locais():
    """Busca noticias de Sorocaba via RSS (G1 Sorocaba) e Web Scraping (Jornal Cruzeiro)"""
    manchetes = []
    
    # 1. Tenta RSS do G1 Sorocaba e Jundiai (Muito estavel no GitHub)
    rss_g1_sorocaba = "https://g1.globo.com/rss/g1/sao-paulo/sorocaba-jundiai/"
    manchetes += buscar_rss(rss_g1_sorocaba, 3)
    
    # 2. Se o RSS falhar, tenta raspagem do Jornal Cruzeiro do Sul
    if not manchetes:
        try:
            url = "https://www.jornalcruzeiro.com.br/"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all('a', href=True)
                
                cont = 0
                for link in links:
                    texto = link.get_text().strip()
                    if len(texto) > 30 and cont < 3: 
                        href = link['href']
                        if not href.startswith('http'):
                            href = url + href
                        manchetes.append(f"- <a href='{href}'>{texto}</a>")
                        cont += 1
        except Exception as e:
            print(f"Erro ao raspar Cruzeiro do Sul: {e}")
            
    if not manchetes:
        manchetes = ["- Nao foi possivel carregar as manchetes atuais."]
        
    return manchetes

if __name__ == "__main__":
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    cot = get_cotacoes()
    noticias = get_noticias()
    man = get_manchetes_locais()
    
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

<b>NOTICIAS LOCAIS (Sorocaba):</b>
{chr(10).join(man)}

Atualizado automaticamente."""

    print(relatorio)
    
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat_id:
        try:
            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": relatorio, "parse_mode": "HTML"},
                timeout=15
            )
            print("Enviado para Telegram!")
        except Exception as e:
            print(f"Erro: {e}")
