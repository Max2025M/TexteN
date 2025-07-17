import asyncio
import logging
from aiohttp import web
from pyppeteer import launch
from pyppeteer.errors import TimeoutError

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')

URL_SERVIDOR = "https://livestream.ct.ws/M/receber.php"

# Flag global para parar loop
parar_loop = False

async def enviar_requisicao():
    global parar_loop
    try:
        logging.info("🚀 Iniciando nova solicitação ao servidor...")

        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()
        await page.goto(URL_SERVIDOR, {'timeout': 30000, 'waitUntil': 'networkidle2'})
        await asyncio.sleep(3)
        content = await page.content()
        await browser.close()

        if "limite" in content.lower():
            logging.warning("🛑 Servidor respondeu com 'limite'. Parando o loop.")
            parar_loop = True
        else:
            logging.info("✅ Solicitação enviada com sucesso.")

    except TimeoutError:
        logging.error("⏰ Tempo excedido ao tentar carregar a página.")
    except Exception as e:
        logging.error(f"❌ Erro ao enviar solicitação: {e}")

async def loop_continuo():
    global parar_loop
    while not parar_loop:
        await enviar_requisicao()
        if not parar_loop:
            logging.info("⏳ Aguardando 60 segundos antes da próxima solicitação...")
            await asyncio.sleep(60)

async def status(request):
    return web.Response(text="🟢 Serviço ativo!")

async def iniciar_app():
    loop_task = asyncio.create_task(loop_continuo())

    app = web.Application()
    app.add_routes([web.get('/', status)])

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host="0.0.0.0", port=8080)
    await site.start()

    logging.info("🌐 Servidor escutando na porta 8080.")
    await loop_task

if __name__ == "__main__":
    try:
        logging.info("🚀 Inicializando aplicação no Render...")
        asyncio.run(iniciar_app())
    except Exception as e:
        logging.error(f"❗ Erro fatal: {e}")
