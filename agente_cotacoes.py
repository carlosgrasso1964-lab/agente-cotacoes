import requests
from bs4 import BeautifulSoup
import datetime
import os

def get_cotacoes():
    # Inicializa com valores padrão caso a API falhe
    dados = {
        'ibovespa': 'Indisponível',
        'dolar': 'Indisponível',
        'euro': 'Indisponível',
        'libra': 'Indisponível',
        'ouro': 'Indisponível',
        'bitcoin': 'Indisponível'
    }
    
    try:
        # Cotações de moedas e Bitcoin via AwesomeAPI
        url_moedas = "https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL,GBP-BRL,BTC-BRL"
        response = requests.get(url_moedas, timeout=10)
        
        if response.status_code == 200:
            res_json = response.json()
            dados['dolar'] = f"R$ {float(res_json['USDBRL']['bid']):.2f}"
            dados['euro'] = f"R$ {float(res_json['EURBRL']['bid']):.2f}"
            dados['libra'] = f"R$ {float(res_json['GBPBRL']['bid']):.2f}"
            dados['bitcoin'] = f"R$ {float(res_json['BTCBRL']['bid']):.2f}"
    except Exception as e:
        print(f"Erro ao buscar moedas: {e}")
        
    try:
        # Exemplo para o Ibovespa (Usando uma alternativa pública ou scraping rápido)
        # Como o Ibovespa não está na AwesomeAPI gratuita de forma direta, 
        # você pode mantê-lo estático ou usar scraping. Para simplificar, deixaremos indicado:
        dados['ibovespa'] = "Consulte Home Broker"
        dados['ouro'] = "Consulte mercado futuro"
    except Exception as e:
        print(f"Erro ao buscar índices: {e}")

    return dados

def get_manchetes_locais():
    manchetes = []
    
    # Exemplo de scraping no Jornal Cruzeiro do Sul
    try:
        url = "https://www.jornalcruzeiro.com.br/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Busca links ou títulos (a estrutura exata depende do HTML do site)
            # Geralmente as manchetes principais estão em tags <a> ou <h2>
            links = soup.find_all('a', href=True)
            
            cont = 0
            for link in links:
                texto = link.get_text().strip()
                # Filtro simples para pegar textos que pareçam manchetes reais
                if len(texto) > 30 and cont < 3: 
                    href = link['href']
                    # Garante que o link seja absoluto
                    if not href.startswith('http'):
                        href = url + href
                    manchetes.append(f"• <a href='{href}'>{texto}</a>")
                    cont += 1
    except Exception as e:
        print(f"Erro ao raspar Cruzeiro do Sul: {e}")
        
    if not manchetes:
        manchetes = ["• Não foi possível carregar as manchetes atuais."]
        
    return manchetes

if __name__ == "__main__":
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    cot = get_cotacoes()
    man = get_manchetes_locais()
    
    # Mudamos a exibição das notícias para aceitar os links formatados em HTML
    relatorio = f"""📊 <b>Relatório Diário - {hoje}</b>

<b>COTAÇÕES:</b>
• Ibovespa: {cot['ibovespa']}
• Dólar: {cot['dolar']}
• Euro: {cot['euro']}
• Libra: {cot['libra']}
• Ouro: {cot['ouro']}
• Bitcoin: {cot['bitcoin']}

<b>NOTÍCIAS LOCAIS (Sorocaba):</b>
{chr(10).join(man)}

<b>Inflação:</b> IPCA ~4,72% (12 meses)

Atualizado automaticamente.
"""
    print(relatorio)
    
    # === CONFIGURAÇÃO TELEGRAM ===
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
        print("⚠️ Token ou chat_id não configurados no ambiente.")
• Bitcoin: {cot['bitcoin']}

<b>NOTÍCIAS LOCAIS (Sorocaba):</b>
{chr(10).join(man)}

<b>Inflação:</b> IPCA ~4,72% (12 meses)

Atualizado automaticamente.
"""
    print(relatorio)
    
    # === CONFIGURAÇÃO TELEGRAM (usando Secrets) ===
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
        print("⚠️ Token ou chat_id não configurados")
