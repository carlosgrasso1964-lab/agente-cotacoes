# -*- coding: utf-8 -*-
import os
import re
import html
import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import xml.etree.ElementTree as ET


def criar_sessao():
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    return session


SESSION = criar_sessao()


def enviar_mensagem_telegram(token, chat_id, texto, preview=True):
    """Funcao generica para envio de mensagens ao Telegram."""
    try:
        r = SESSION.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": texto,
                "parse_mode": "HTML",
                "disable_web_page_preview": not preview
            },
            timeout=20,
        )
        print(f"[DEBUG] Telegram API status: {r.status_code}")
        print(f"[DEBUG] Telegram API response: {r.text}")
        return r.status_code == 200 and r.json().get("ok")
    except Exception as e:
        print(f"[DEBUG] Erro ao conectar com API do Telegram: {e}")
        return False


def limpar_texto(texto):
    if not texto:
        return ""
    texto_sem_html = re.sub(r'<[^<]+?>', '', texto)
    return html.escape(texto_sem_html.strip())


def buscar_rss(url, limite=3):
    noticias = []
    try:
        r = SESSION.get(url, timeout=20)
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            for item in root.findall('.//item')[:limite]:
                titulo = item.findtext('title', '')
                link = item.findtext('link', '')
                if titulo and link:
                    titulo_limpo = limpar_texto(titulo)[:120]
                    link_seguro = html.escape(link.strip())
                    noticias.append(f"- <a href='{link_seguro}'>{titulo_limpo}</a>")
    except Exception as e:
        print(f"Erro ao buscar RSS ({url}): {e}")
    return noticias


def get_internacionais():
    n = []
    n += buscar_rss("https://g1.globo.com/mundo/rss/", 3)
    n += buscar_rss("https://feeds.bbci.co.uk/portuguese/rss.xml", 3)
    return n


def get_nacionais():
    n = []
    n += buscar_rss("https://g1.globo.com/rss/g1/", 2)
    n += buscar_rss("https://www.cnnbrasil.com.br/feed/", 2)
    return n


def get_locais():
    n = []
    try:
        url = "https://news.google.com/rss/search?q=Sorocaba&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        r = SESSION.get(url, timeout=20)
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            for item in root.findall('.//item')[:4]:
                titulo = item.findtext('title', '')
                if titulo:
                    titulo_limpo = re.sub(r"\s*-\s*[^-]*$", "", titulo).strip()
                    titulo_seguro = limpar_texto(titulo_limpo)[:90]
                    n.append(f"- {titulo_seguro}")
    except Exception as e:
        print(f"Erro ao buscar noticias locais: {e}")
    return n


def main():
    # Prioridade: TELEGRAM_TOKEN / TELEGRAM_CHAT_ID (GitHub Actions secrets),
    # fallback: TTK / TID (variaveis do Windows definidas pelo Carlos).
    print(f"[DEBUG] TELEGRAM_TOKEN definido: {'TELEGRAM_TOKEN' in os.environ}")
    print(f"[DEBUG] TELEGRAM_CHAT_ID definido: {'TELEGRAM_CHAT_ID' in os.environ}")
    print(f"[DEBUG] TTK definido: {'TTK' in os.environ}")
    print(f"[DEBUG] TID definido: {'TID' in os.environ}")
    
    token = os.environ.get("TELEGRAM_TOKEN") or os.environ.get("TTK", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("TID", "")
    
    print(f"[DEBUG] token length: {len(token)}")
    print(f"[DEBUG] chat_id length: {len(chat_id)}")
    if token:
        print(f"[DEBUG] token prefix: {token[:10]}...")
    if chat_id:
        print(f"[DEBUG] chat_id: {chat_id}")
    
    if not token or not chat_id:
        print("ERRO: variaveis TELEGRAM_TOKEN/TELEGRAM_CHAT_ID (ou TTK/TID no Windows) nao definidas.")
        print("No GitHub Actions defina os secrets; no Windows defina TTK/TID em Variaveis de Ambiente (usuario).")
        return 1
    if "SEU_" in token or "SEU_" in chat_id or token in ("TTK", "TID"):
        print("ERRO: variavel ainda com placeholder (SEU_/nome). Atualize.")
        return 1

    try:
        print("[DEBUG] Iniciando busca de noticias...")
        print("Buscando noticias para o Journal...")
        print("[DEBUG] Chamando get_internacionais()...")
        internacionais = get_internacionais()
        print(f"[DEBUG] Internacionais: {len(internacionais)} itens")
        print("[DEBUG] Chamando get_nacionais()...")
        nacionais = get_nacionais()
        print(f"[DEBUG] Nacionais: {len(nacionais)} itens")
        print("[DEBUG] Chamando get_locais()...")
        locais = get_locais()
        print(f"[DEBUG] Locais: {len(locais)} itens")

        # VERIFICACAO DE FALHA TOTAL DOS FEEDS
        if not internacionais and not nacionais and not locais:
            print("ALERTA: Todas as fontes de noticias falharam.")
            msg_alerta = (
            "⚠️ <b>Alerta Journal Diario</b>\n\n"
            "Nao foi possivel carregar nenhuma noticia no boletim de hoje. "
            "Todas as fontes de RSS (G1, BBC, CNN, Google News) falharam ou timeout."
            )
            enviar_mensagem_telegram(token, chat_id, msg_alerta, preview=False)
            print("Alerta enviado. Workflow termina com sucesso (nao falha o CI).")
            return 0
        
        # Tratamento individual de secoes vazias
        list_inter = internacionais if internacionais else ["- <i>Nao foi possivel carregar noticias internacionais.</i>"]
        list_nac = nacionais if nacionais else ["- <i>Nao foi possivel carregar noticias nacionais.</i>"]
        list_loc = locais if locais else ["- <i>Nao foi possivel carregar noticias locais.</i>"]

        hoje = datetime.date.today().strftime("%d/%m/%Y")
        jornal = f"""📰 <b>Journal Diario - {hoje}</b>

🌍 <b>INTERNACIONAIS:</b>
{chr(10).join(list_inter)}

📰 <b>NACIONAIS:</b>
{chr(10).join(list_nac)}

📍 <b>LOCAIS (Sorocaba):</b>
{chr(10).join(list_loc)}

Atualizado automaticamente."""

        print("Enviando Journal ao Telegram...")
        sucesso = enviar_mensagem_telegram(token, chat_id, jornal, preview=False)
        if sucesso:
            print("Journal enviado com sucesso!")
            return 0
        else:
            print("Falha na resposta da API do Telegram.")
            return 1

    except Exception as err_critico:
        # CAPTURA DE ERRO INESPERADO NO SCRIPT
        print(f"Erro critico na execucao: {err_critico}")
        msg_erro = f"🚨 <b>Falha no Workflow do Journal</b>\n\nErro: <code>{limpar_texto(str(err_critico))}</code>"
        enviar_mensagem_telegram(token, chat_id, msg_erro, preview=False)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
