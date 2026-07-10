# agente-cotacoes
Agente diário de cotações e notícias
# Configuração Telegram (preencha depois)
  
  # === CONFIGURAÇÃO TELEGRAM ===
    token = "8992452932:AAHk83jULYSjGkhgHnOZETLgWng6wmi2b54"
    chat_id = "978630915"
    
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": relatorio, "parse_mode": "HTML"}
        )
        print("Mensagem enviada para Telegram!")
    except:
        print("Erro ao enviar Telegram")
