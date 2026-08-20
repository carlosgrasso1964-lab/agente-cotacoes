# -*- coding: utf-8 -*-
"""Envia relatorio de cotacoes + noticias + graficos para o Telegram.

O token e o chat_id vem das VARIÁVEIS DE AMBIENTE do Windows
(TELEGRAM_TOKEN e TELEGRAM_CHAT_ID), nunca de arquivo.

Uso: python enviar_telegram.py
"""
import os
import requests
from agente_cotacoes import get_cotacoes, get_noticias, get_manchetes_locais

PASTA_GRAFICOS = "graficos"


def carregar_env():
    """Le pares chave=valor do .env (ignorando comentarios)."""
    env = {}
    if not os.path.exists(ARQUIVO_ENV):
        print("ERRO: arquivo .env nao encontrado.")
        return env
    with open(ARQUIVO_ENV, encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            k, v = linha.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def montar_relatorio(cot):
    """Monta o texto do relatorio (como o original do Telegram)."""
    import datetime
    hoje = datetime.date.today().strftime("%d/%m/%Y")
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
    return relatorio


def enviar_texto(token, chat_id, texto):
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": texto, "parse_mode": "HTML"},
        timeout=20,
    )
    if r.status_code == 200 and r.json().get("ok"):
        print("  - Relatorio em texto enviado ✓")
        return True
    print(f"  - Falha ao enviar texto: {r.json().get('description')}")
    return False


def enviar_fotos(token, chat_id):
    """Envia todos os PNGs da pasta de graficos como fotos."""
    if not os.path.isdir(PASTA_GRAFICOS):
        print("  - Pasta de graficos nao encontrada; nenhuma foto enviada.")
        return 0
    pngs = sorted(
        [f for f in os.listdir(PASTA_GRAFICOS) if f.lower().endswith(".png")]
    )
    enviadas = 0
    for png in pngs:
        caminho = os.path.join(PASTA_GRAFICOS, png)
        try:
            with open(caminho, "rb") as f:
                r = requests.post(
                    f"https://api.telegram.org/bot{token}/sendPhoto",
                    data={"chat_id": chat_id},
                    files={"photo": (png, f)},
                    timeout=30,
                )
            if r.status_code == 200 and r.json().get("ok"):
                print(f"  - Foto enviada: {png} ✓")
                enviadas += 1
            else:
                print(f"  - Falha na foto {png}: {r.json().get('description')}")
        except Exception as e:
            print(f"  - Erro na foto {png}: {e}")
    return enviadas


def main():
    # Valores vem das VARIÁVEIS DE AMBIENTE do Windows (nunca de arquivo).
    # ESCOLHIDO: o Carlos definiu no Windows as variaveis TTK (token) e TID (chat_id).
    token = os.environ.get("TTK", "")
    chat_id = os.environ.get("TID", "")
    if not token or not chat_id:
        print("ERRO: variaveis TTK e/ou TID nao definidas no Windows.")
        print("Defina-as: Painel de Controle > Sistema > Variaveis de Ambiente (usuario) e reinicie o terminal.")
        return 1
    if "SEU_" in token or "SEU_" in chat_id or token == "TTK" or chat_id == "TID":
        print("ERRO: variavel ainda com placeholder (SEU_/nome). Atualize no Windows.")
        return 1

    print("Buscando cotacoes e noticias...")
    cot, _ = get_cotacoes()

    print("Enviando para o Telegram:")
    ok_texto = enviar_texto(token, chat_id, montar_relatorio(cot))
    n_fotos = enviar_fotos(token, chat_id)

    print(f"\nResumo: texto={'OK' if ok_texto else 'FALHA'}, fotos enviadas={n_fotos}")
    if ok_texto and n_fotos > 0:
        print("SUCESSO: relatorio + graficos enviados ao Telegram!")
    else:
        print("AVISO: houve falha parcial; verifique acima.")


if __name__ == "__main__":
    main()