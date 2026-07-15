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
    
    # Adicionando User-Agent para evitar bloqueio (HTTP 429) no GitHub Actions
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        # Cotacoes de moedas e Bitcoin via AwesomeAPI
        url_moedas = "https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL,GBP-BRL,BTC-BRL"
        response = requests.get(url_moedas, headers=headers, timeout=15)
        
        if response.status_code == 200:
            res_json = response.json()
            dados['dolar'] = f"R$ {float(res_json['USDBRL']['bid']):.2f}"
            dados['euro'] = f"R$ {float(res_json['EURBRL']['bid']):.2f}"
            dados['libra'] = f"R$ {float(res_json['GBPBRL']['bid']):.2f}"
            dados['bitcoin'] = f"R$ {float(res_json['BTCBRL']['bid']):.2f}"
        else:
            print(f"Erro na API de moedas. Status Code: {response.status_code}")
    except Exception as e:
        print(f"Erro ao buscar moedas: {e}")
        
    try:
        dados['ibovespa'] = "Consulte Home Broker"
        dados['ouro'] = "Consulte mercado futuro"
    except Exception as e:
        print(f"Erro ao buscar indices: {e}")

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
