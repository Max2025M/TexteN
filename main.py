import asyncio
from pyppeteer import launch
from datetime import datetime
import pytz
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
)

URL = "https://livestream.ct.ws/M/receber.php"
INTERVALO_SEGUNDOS = 60  # 1 minuto

async def enviar_solicitacao():
    browser = None
    try:
        browser = await launch(headless=True, args=['--no-sandbox'])
        page = await browser.newPage()
        logging.info(f"Iniciando acesso ao {URL}")

        # Navega e espera a rede ficar ociosa, para que scripts JS sejam executados
        response = await page.goto(URL, waitUntil='networkidle2', timeout=15000)

        if response is None:
            logging.warning("⚠️ Sem resposta do servidor (timeout ou falha).")
            return False

        status = response.status
        content = await page.content()

        logging.info(f"Status da resposta HTTP: {status}")

        if "OK" in content:
            logging.info("✅ Resposta OK recebida, continuar enviando solicitações.")
            return True
        else:
            logging.info("⚠️ Resposta diferente de OK (possivelmente fim do horário).")
            return False

    except Exception as e:
        logging.error(f"❌ Erro ao acessar o servidor: {e}")
        return False

    finally:
        if browser:
            try:
                await browser.close()
            except Exception as e:
                logging.warning(f"⚠️ Erro ao fechar o navegador: {e}")

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
