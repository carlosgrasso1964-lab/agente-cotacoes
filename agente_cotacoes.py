# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
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
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # 1. Moedas (USD, EUR, GBP) via ExchangeRate-API (Altamente estavel no GitHub Actions)
    try:
        url_cambio = "https://open.er-api.com/v6/latest/USD"
        response = requests.get(url_cambio, headers=headers, timeout=15)
        
        if response.status_code == 200:
            res_json = response.json()
            rates = res_json.get('rates', {})
            
            usd_brl = rates.get('BRL')
            eur_usd = rates.get('EUR')
            gbp_usd = rates.get('GBP')
            
            if usd_brl:
                dados['dolar'] = f"R$ {usd_brl:.2f}"
                # Calcula Euro e Libra baseados na proporcao do Dolar
                if eur_usd:
                    dados['euro'] = f"R$ {(usd_brl / eur_usd):.2f}"
                if gbp_usd:
                    dados['libra'] = f"R$ {(usd_brl / gbp_usd):.2f}"
            else:
                print("Erro: Nao foi possivel extrair a taxa de BRL da API.")
        else:
            print(f"Erro na API de Cambio. Status: {response.status_code}")
    except Exception as e:
        print(f"Erro ao buscar moedas: {e}")
        
    # 2. Bitcoin via Coinbase (API publica extremamente robusta)
    try:
        url_btc = "https://api.coinbase.com/v2/prices/BTC-BRL/spot"
        response = requests.get(url_btc, headers=headers, timeout=15)
        
        if response.status_code == 200:
            res_json = response.json()
            btc_brl = float(res_json['data']['amount'])
            dados['bitcoin'] = f"R$ {btc_brl:.2f}"
        else:
            print(f"Erro na API da Coinbase. Status: {response.status_code}")
    except Exception as e:
        print(f"Erro ao buscar Bitcoin: {e}")
        
    # Indices estaticos/manuais
    dados['ibovespa'] = "Consulte Home Broker"
    dados['ouro'] = "Consulte mercado futuro"

    return dados

def get_manchetes_locais():
    manchetes = []
    
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
    man = get_manchetes_locais()
    
    relatorio = f"""📊 <b>Relatorio Diario - {hoje}</b>

<b>COTACOES:</b>
- Ibovespa: {cot['ibovespa']}
- Dolar: {cot['dolar']}
- Euro: {cot['euro']}
- Libra: {cot['libra']}
- Ouro: {cot['ouro']}
- Bitcoin: {cot['bitcoin']}

<b>NOTICIAS LOCAIS (Sorocaba):</b>
{chr(10).join(man)}

<b>Inflacao:</b> IPCA ~4,72% (12 meses)

Atualizado automaticamente.
"""
    print(relatorio)
    
    # === CONFIGURACAO TELEGRAM ===
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if token and chat_id:
        try:
            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": relatorio, "parse_mode": "HTML"}
            )
            print("✅ Mensagem enviada para Telegram!")
        except Exception as e:
            print(f"Erro ao enviar: {e}")
    else:
        print("⚠️ Token ou chat_id nao configurados no ambiente.")
