import asyncio
from threading import Thread
from flask import Flask
from pyppeteer import launch
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

URL = "https://livestream.ct.ws/M/receber.php"
INTERVALO_SEGUNDOS = 180  # 3 minutos

app = Flask(__name__)

async def enviar_solicitacao():
    browser = await launch(headless=True, args=['--no-sandbox'])
    page = await browser.newPage()

    try:
        logging.info(f"Iniciando acesso ao {URL}")
        response = await page.goto(URL, timeout=15000)  # 15s timeout

        if not response:
            logging.warning("Sem resposta do servidor (timeout ou falha).")
            await browser.close()
            return False

        status = response.status
        texto = await page.content()

        logging.info(f"Status da resposta: {status}")

        if "OK" in texto:
            logging.info("Resposta OK recebida, continuar executando.")
            await browser.close()
            return True
        else:
            logging.info("Resposta diferente de OK (possivelmente fim do horário).")
            await browser.close()
            return False

    except Exception as e:
        logging.error(f"Erro ao acessar o servidor: {e}")
        await browser.close()
        return False

async def loop_pyppeteer():
    while True:
        continuar = await enviar_solicitacao()
        if not continuar:
            logging.info("Parando o loop - servidor não respondeu OK.")
            break
        logging.info(f"Aguardando {INTERVALO_SEGUNDOS} segundos para próxima requisição...")
        await asyncio.sleep(INTERVALO_SEGUNDOS)

def start_loop():
    asyncio.run(loop_pyppeteer())

@app.route('/')
def index():
    return "Serviço ativo. Pyppeteer rodando em background."

if __name__ == "__main__":
    # Inicia loop Pyppeteer em thread separada para não travar Flask
    t = Thread(target=start_loop)
    t.start()

    # Roda o Flask no host 0.0.0.0 na porta 10000 (Render prefere porta 10000+)
    app.run(host="0.0.0.0", port=10000)
