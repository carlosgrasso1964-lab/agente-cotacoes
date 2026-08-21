# -*- coding: utf-8 -*-
"""Journal Diario de Noticias — envia boletim de noticias ao Telegram.

Busca noticias de:
  - Internacionais: G1 Mundo + BBC Brasil
  - Nacionais: G1 + CNN Brasil
  - Locais: Sorocaba (Google News)

Envia como MENSAGEM de texto ao Telegram (sem cotacoes).
Rodado diariamente pelo GitHub Actions (workflow journal-diario.yml).

Usa os secrets do GitHub: TELEGRAM_TOKEN e TELEGRAM_CHAT_ID.
"""
import os
import re
import datetime
import requests
import xml.etree.ElementTree as ET


def esc(texto):
    """Escapa caracteres HTML para o Telegram (evita quebras de parse)."""
    return (texto.replace("&", "&amp;")
                 .replace("<", "&lt;")
                 .replace(">", "&gt;"))


def buscar_rss(url, limite=3):
    """Busca noticias de um feed RSS e retorna lista de titulos com links."""
    noticias = []
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}, timeout=15)
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            for item in root.findall('.//item')[:limite]:
                titulo = item.findtext('title', '').strip()
                link = item.findtext('link', '').strip()
                if titulo:
                    noticias.append(f"- <a href='{esc(link)}'>{esc(titulo[:120])}</a>")
    except Exception as e:
        print(f"Erro ao buscar RSS ({url}): {e}")
    return noticias


def get_internacionais():
    """Noticias internacionais em portugues (G1 Mundo + BBC Brasil)."""
    n = []
    n += buscar_rss("https://g1.globo.com/mundo/rss/", 3)
    n += buscar_rss("https://feeds.bbci.co.uk/portuguese/rss.xml", 3)
    if not n:
        n = ["- Nao foi possivel carregar noticias internacionais."]
    return n


def get_nacionais():
    """Noticias nacionais (G1 + CNN Brasil)."""
    n = []
    n += buscar_rss("https://g1.globo.com/rss/g1/", 2)
    n += buscar_rss("https://www.cnnbrasil.com.br/feed/", 2)
    if not n:
        n = ["- Nao foi possivel carregar noticias nacionais."]
    return n


def get_locais():
    """Noticias locais de Sorocaba (Google News RSS) com links limpos."""
    n = []
    try:
        url = "https://news.google.com/rss/search?q=Sorocaba&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}, timeout=15)
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            for item in root.findall('.//item')[:4]:
                titulo = item.findtext('title', '').strip()
                if titulo:
                    # Limpa prefixos padrao do Google News (ex: " - G1", " - ...")
                    import re
                    titulo_limpo = re.sub(r"\s*-\s*[^-]*$", "", titulo).strip()
                    # Locais: enviar como texto puro (sem link), pois as URLs do
                    # Google News contem parenteses/apostrofes que quebram o JSON
                    # parse_mode=HTML do Telegram.
                    n.append(f"- {esc(titulo_limpo[:90])}")
    except Exception as e:
        print(f"Erro ao buscar noticias locais: {e}")
    if not n:
        n = ["- Nao foi possivel carregar noticias locais."]
    return n


def montar_journal():
    """Monta o texto do Journal Diario de Noticias."""
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    internacionais = get_internacionais()
    nacionais = get_nacionais()
    locais = get_locais()

    jornal = f"""📰 <b>Journal Diario - {hoje}</b>

🌍 <b>INTERNACIONAIS:</b>
{chr(10).join(internacionais)}

📰 <b>NACIONAIS:</b>
{chr(10).join(nacionais)}

📍 <b>LOCAIS (Sorocaba):</b>
{chr(10).join(locais)}

Atualizado automaticamente."""
    return jornal


def main():
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("ERRO: variaveis TELEGRAM_TOKEN/TELEGRAM_CHAT_ID nao definidas (rodando fora do GitHub Actions?).")
        return 1

    print("Buscando noticias para o Journal...")
    texto = montar_journal()

    print("Enviando Journal ao Telegram...")
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": texto, "parse_mode": "HTML"},
        timeout=20,
    )
    if r.status_code == 200 and r.json().get("ok"):
        print("Journal enviado com sucesso!")
        return 0
    print(f"Falha ao enviar: {r.status_code} {r.text[:300]}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())