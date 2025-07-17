import asyncio
import logging
from pyppeteer import launch
from pyppeteer.errors import TimeoutError

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')

URL_SERVIDOR = "https://livestream.ct.ws/M/receber.php"

async def enviar_requisicao():
    try:
        logging.info("🚀 Iniciando nova solicitação ao servidor...")

        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()

        # Aguarda resposta completa e execução de JS
        await page.goto(URL_SERVIDOR, {
            'timeout': 30000,
            'waitUntil': 'networkidle2'  # aguarda até que nenhuma requisição esteja ativa
        })

        # Espera 3 segundos extras para garantir execução de qualquer JS injectado
        await asyncio.sleep(3)

        content = await page.content()

        if "limite" in content.lower():
            logging.warning("🛑 Servidor respondeu com 'limite'. Encerrando requisições.")
            await browser.close()
            return False  # sinaliza para parar o loop

        logging.info("✅ Solicitação enviada com sucesso.")
        await browser.close()
        return True

    except TimeoutError:
        logging.error("⏰ Tempo excedido ao tentar carregar a página.")
        return True  # continua tentando
    except Exception as e:
        logging.error(f"❌ Erro ao enviar solicitação: {e}")
        return True  # continua tentando

async def loop_continuo():
    while True:
        continuar = await enviar_requisicao()
        if not continuar:
            break
        logging.info("⏳ Aguardando 60 segundos antes da próxima solicitação...")
        await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        logging.info("🟢 Iniciando ciclo de requisições automáticas.")
        asyncio.run(loop_continuo())
    except KeyboardInterrupt:
        logging.warning("🛑 Interrompido manualmente.")
    except Exception as e:
        logging.error(f"❗ Erro fatal: {e}")
