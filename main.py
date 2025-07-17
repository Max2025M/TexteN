import asyncio
import logging
from pyppeteer import launch

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')

URL_SERVIDOR = "https://livestream.ct.ws/M/receber.php"

async def enviar_requisicao():
    try:
        browser = await launch(headless=True, args=['--no-sandbox'])
        page = await browser.newPage()
        await page.goto(URL_SERVIDOR, timeout=30000)  # 30s timeout

        content = await page.content()

        if "limite" in content.lower():
            logging.warning("🛑 Servidor respondeu com 'limite'. Encerrando.")
            await browser.close()
            return False  # sinaliza para parar o loop

        logging.info("✅ Solicitação enviada com sucesso")
        await browser.close()
        return True  # continua

    except Exception as e:
        logging.error(f"❌ Erro ao enviar solicitação: {e}")
        return True  # continua tentando mesmo com erro

async def loop_continuo():
    while True:
        continuar = await enviar_requisicao()
        if not continuar:
            break
        await asyncio.sleep(60)  # espera 1 minuto antes da próxima

if __name__ == "__main__":
    try:
        asyncio.run(loop_continuo())
    except KeyboardInterrupt:
        logging.warning("🛑 Interrompido manualmente.")
    except Exception as e:
        logging.error(f"Erro fatal: {e}")

