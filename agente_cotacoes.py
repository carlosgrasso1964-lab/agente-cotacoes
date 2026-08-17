# -*- coding: utf-8 -*-
import requests
import datetime
import os
import xml.etree.ElementTree as ET
from openpyxl import Workbook, load_workbook

ARQUIVO_PLANILHA = "cotacoes_historico.xlsx"


def get_cotacoes():
    dados = {
        'ibovespa': 'Indisponivel',
        'dolar': 'Indisponivel',
        'euro': 'Indisponivel',
        'libra': 'Indisponivel',
        'ouro': 'Indisponivel',
        'bitcoin': 'Indisponivel'
    }
    numeros = {}  # valores crus para gravar na planilha/grafico
    h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    # USD/BRL
    try:
        r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/BRL%3DX?interval=1d&range=1d", headers=h, timeout=15)
        if r.status_code == 200:
            usd = r.json()['chart']['result'][0]['meta']['regularMarketPrice']
            dados['dolar'] = f"R$ {usd:.2f}"
            dados['usd'] = usd
            numeros['dolar'] = round(float(usd), 4)
    except:
        pass

    # EUR/BRL
    try:
        r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/EURBRL%3DX?interval=1d&range=1d", headers=h, timeout=15)
        if r.status_code == 200:
            eur = r.json()['chart']['result'][0]['meta']['regularMarketPrice']
            dados['euro'] = f"R$ {eur:.2f}"
            numeros['euro'] = round(float(eur), 4)
    except:
        pass

    # GBP/BRL
    try:
        r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/GBPBRL%3DX?interval=1d&range=1d", headers=h, timeout=15)
        if r.status_code == 200:
            gbp = r.json()['chart']['result'][0]['meta']['regularMarketPrice']
            dados['libra'] = f"R$ {gbp:.2f}"
            numeros['libra'] = round(float(gbp), 4)
    except:
        pass

    # Bitcoin
    try:
        r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD?interval=1d&range=1d", headers=h, timeout=15)
        if r.status_code == 200:
            btc = r.json()['chart']['result'][0]['meta']['regularMarketPrice']
            usd = numeros.get('dolar', dados.get('usd', 5.0))
            dados['bitcoin'] = f"R$ {(btc * usd):,.2f}"
            numeros['bitcoin'] = round(float(btc * usd), 2)
    except:
        pass

    # Ibovespa
    try:
        r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/%5EBVSP?interval=1d&range=1d", headers=h, timeout=15)
        if r.status_code == 200:
            ibov = r.json()['chart']['result'][0]['meta']['regularMarketPrice']
            dados['ibovespa'] = f"{ibov:,.2f} pts"
            numeros['ibovespa'] = round(float(ibov), 2)
    except:
        pass

    # Ouro
    try:
        r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/GC%3DF?interval=1d&range=1d", headers=h, timeout=15)
        if r.status_code == 200:
            gold = r.json()['chart']['result'][0]['meta']['regularMarketPrice']
            usd = numeros.get('dolar', dados.get('usd', 5.0))
            dados['ouro'] = f"R$ {(gold * usd):,.2f}/oz"
            numeros['ouro'] = round(float(gold * usd), 2)
    except:
        pass

    return dados, numeros


def gravar_historico(numeros):
    """Acrescenta uma linha c/ as cotações na planilha acumulativa (xlsx)."""
    if not numeros:
        print("Nenhuma cotacao numerica disponivel; nada gravado.")
        return

    # Data do ultimo fechamento = dia anterior a execucao (cron roda antes da abertura)
    data_ref = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%d/%m/%Y")

    cabecalho = ["Data", "Dolar", "Euro", "Libra", "Bitcoin", "Ibovespa", "Ouro"]
    linha = [
        data_ref,
        numeros.get('dolar', ''),
        numeros.get('euro', ''),
        numeros.get('libra', ''),
        numeros.get('bitcoin', ''),
        numeros.get('ibovespa', ''),
        numeros.get('ouro', ''),
    ]

    try:
        if os.path.exists(ARQUIVO_PLANILHA):
            wb = load_workbook(ARQUIVO_PLANILHA)
            ws = wb.active
        else:
            wb = Workbook()
            ws = wb.active
            ws.title = "Cotacoes"
            ws.append(cabecalho)
        ws.append(linha)
        wb.save(ARQUIVO_PLANILHA)
        print(f"Historico gravado em {ARQUIVO_PLANILHA} (linha {ws.max_row})")
    except Exception as e:
        print(f"Erro ao gravar historico: {e}")


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
    """Busca noticias de Sorocaba via Google News RSS (sempre atualizado)"""
    manchetes = []

    try:
        url = "https://news.google.com/rss/search?q=Sorocaba&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}, timeout=15)
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            for item in root.findall('.//item')[:4]:
                titulo = item.findtext('title', '').strip()
                link = item.findtext('link', '').strip()
                if titulo:
                    manchetes.append(f"- <a href='{link}'>{titulo[:100]}</a>")
    except Exception as e:
        print(f"Erro ao buscar noticias locais: {e}")

    if not manchetes:
        manchetes = ["- Nao foi possivel carregar as manchetes locais."]

    return manchetes


if __name__ == "__main__":
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    cot, numeros = get_cotacoes()
    gravar_historico(numeros)

    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    # Só monta o relatorio/busca notícias se for enviar pro Telegram
    if token and chat_id:
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

        try:
            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": relatorio, "parse_mode": "HTML"},
                timeout=15
            )
            print("Enviado para Telegram!")
        except Exception as e:
            print(f"Erro: {e}")
    else:
        print("Modo local (sem Telegram): cotacao gravada, noticias ignoradas.")