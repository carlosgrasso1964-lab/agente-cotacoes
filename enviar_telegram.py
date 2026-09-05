# -*- coding: utf-8 -*-
"""Envia relatório de cotações + gráficos para o Telegram (sem notícias).

O token e o chat_id vem das VARIÁVEIS DE AMBIENTE do Windows
(TTK e TID), nunca de arquivo.

Uso: python enviar_telegram.py
"""
import os
import requests
from agente_cotacoes import get_cotacoes

PASTA_GRAFICOS = "graficos"


def montar_relatorio(cot):
    """Monta o texto do relatório (apenas cotações)."""
    import datetime
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    relatorio = f"""📊 <b>Relatório de Cotações - {hoje}</b>

<b>COTAÇÕES:</b>
- Ibovespa: {cot['ibovespa']}
- Dolar: {cot['dolar']}
- Euro: {cot['euro']}
- Libra: {cot['libra']}
- Ouro: {cot['ouro']}
- Bitcoin: {cot['bitcoin']}

Atualizado automaticamente."""
    return relatorio


def enviar_texto(token, chat_id, texto):
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": texto, "parse_mode": "HTML"},
        timeout=20,
    )
    if r.status_code == 200 and r.json().get("ok"):
        print("  - Relatório em texto enviado ✓")
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
    # Token e chat_id vêm das variáveis de ambiente (nunca de arquivo).
    # Prioridade: TELEGRAM_TOKEN / TELEGRAM_CHAT_ID (GitHub Actions secrets),
    # fallback: TTK / TID (variáveis do Windows definidas pelo Carlos).
    token = os.environ.get("TELEGRAM_TOKEN") or os.environ.get("TTK", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("TID", "")
    if not token or not chat_id:
        print("ERRO: variaveis TELEGRAM_TOKEN/TELEGRAM_CHAT_ID (ou TTK/TID no Windows) nao definidas.")
        print("No GitHub Actions defina os secrets; no Windows defina TTK/TID em Variaveis de Ambiente (usuario).")
        return 1
    if "SEU_" in token or "SEU_" in chat_id or token in ("TTK", "TID"):
        print("ERRO: variavel ainda com placeholder (SEU_/nome). Atualize.")
        return 1

    print("Buscando cotações...")
    cot, _ = get_cotacoes()

    print("Enviando para o Telegram:")
    ok_texto = enviar_texto(token, chat_id, montar_relatorio(cot))
    n_fotos = enviar_fotos(token, chat_id)

    print(f"\nResumo: texto={'OK' if ok_texto else 'FALHA'}, fotos enviadas={n_fotos}")
    if ok_texto and n_fotos > 0:
        print("SUCESSO: relatório + gráficos enviados ao Telegram!")
    else:
        print("AVISO: houve falha parcial; verifique acima.")


if __name__ == "__main__":
    main()