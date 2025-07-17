import asyncio
from pyppeteer import launch
from datetime import datetime
import pytz
import logging

# Configura o logger para exibir mensagens no console
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
)

URL = "https://livestream.ct.ws/M/receber.php"
INTERVALO_SEGUNDOS = 60  # 1 minuto

async def enviar_solicitacao():
    try:
        browser = await launch(headless=True, args=['--no-sandbox'])
        page = await browser.newPage()
        logging.info(f"Iniciando acesso ao {URL}")
        response = await page.goto(URL, timeout=15000)  # 15 segundos timeout

        if not response:
            logging.warning("⚠️ Sem resposta do servidor (timeout ou falha).")
            await browser.close()
            return False

        status = response.status
        texto = await page.content()

        logging.info(f"Status da resposta HTTP: {status}")

        if "OK" in texto:
            logging.info("✅ Resposta OK recebida, continuar enviando solicitações.")
            await browser.close()
            return True
        else:
            logging.info("⚠️ Resposta diferente de OK (possivelmente fim do horário).")
            await browser.close()
            return False

    except Exception as e:
        logging.error(f"❌ Erro ao acessar o servidor: {e}")
        return False

async def loop_pyppeteer():
    while True:
        continuar = await enviar_solicitacao()
        if not continuar:
            logging.info("⏹️ Parando o loop - servidor não respondeu OK.")
            break
        logging.info(f"⏳ Aguardando {INTERVALO_SEGUNDOS} segundos para a próxima requisição...")
        await asyncio.sleep(INTERVALO_SEGUNDOS)

if __name__ == "__main__":
    asyncio.run(loop_pyppeteer())
