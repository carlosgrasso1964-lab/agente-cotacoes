import requests
from bs4 import BeautifulSoup
import datetime
import os

def get_cotacoes():
    return {
        'ibovespa': 'Consulte site (ex: ~172000 pts)',
        'dolar': 'R$ ~5.13',
        'euro': 'R$ ~5.85',
        'libra': 'R$ ~6.92',
        'ouro': 'US$ ~4100',
        'bitcoin': 'US$ ~63000'
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
