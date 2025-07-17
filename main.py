import os
import asyncio
import logging
from aiohttp import web
from pyppeteer import launch
from pyppeteer.errors import TimeoutError

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')

URL_SERVIDOR = "https://livestream.ct.ws/M/receber.php"

async def enviar_requisicao():
    try:
        logging.info("🚀 Iniciando nova solicitação ao servidor...")

        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()

        await page.goto(URL_SERVIDOR, {
            'timeout': 30000,
            'waitUntil': 'networkidle2'
        })

        await asyncio.sleep(3)  # espera extra para JS

        content = await page.content()

        await browser.close()

        if "limite" in content.lower():
            logging.warning("🛑 Servidor respondeu com 'limite'. Encerrando requisições.")
            return False

        logging.info("✅ Solicitação enviada com sucesso.")
        return True

    except TimeoutError:
        logging.error("⏰ Tempo excedido ao tentar carregar a página.")
        return True
    except Exception as e:
        logging.error(f"❌ Erro ao enviar solicitação: {e}")
        return True

async def loop_continuo():
    while True:
        continuar = await enviar_requisicao()
        if not continuar:
            break
        logging.info("⏳ Aguardando 60 segundos antes da próxima solicitação...")
        await asyncio.sleep(60)

async def handle(request):
    return web.Response(text="Render: Serviço ativo.\n")

async def main():
    # Start background task
    asyncio.create_task(loop_continuo())

    # Setup web server
    app = web.Application()
    app.router.add_get('/', handle)

    # Porta definida pelo Render (ou padrão 10000)
    port = int(os.environ.get('PORT', 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    logging.info(f"🔵 Servidor web rodando em http://0.0.0.0:{port}")
    await site.start()

    # Mantém o servidor rodando
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.warning("🛑 Interrompido manualmente.")
    except Exception as e:
        logging.error(f"Erro fatal: {e}")
