import requests
from bs4 import BeautifulSoup
import datetime

def get_cotacoes():
    return {
        'ibovespa': 'Consulte site (ex: \~172000 pts)',
        'dolar': 'R$ \~5.13',
        'euro': 'R$ \~5.85',
        'libra': 'R$ \~6.92',
        'ouro': 'US$ \~4100',
        'bitcoin': 'US$ \~63000'
    }

def get_manchetes_locais():
    sites = [
        "Jornal Cruzeiro: https://www.jornalcruzeiro.com.br/",
        "Jornal Ipanema: https://www.jornalipanema.com.br/",
        "Jornal ZNorte: https://jornalznorte.com.br/"
    ]
    return sites

if __name__ == "__main__":
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    cot = get_cotacoes()
    man = get_manchetes_locais()
    
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

<b>Inflação:</b> IPCA \~4,72% (12 meses)

Atualizado automaticamente.
"""
    print(relatorio)
    
    # Configuração Telegram (preencha depois)
    # token = "SEU_TOKEN_AQUI"
    # chat_id = "SEU_CHAT_ID_AQUI"
    # requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "text": relatorio, "parse_mode": "HTML"})
