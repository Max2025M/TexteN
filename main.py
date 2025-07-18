import os
import asyncio
import logging
from aiohttp import web
from pyppeteer import launch
from pyppeteer.errors import TimeoutError

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')

URL_SERVIDOR = "https://livestream.ct.ws/M/receber.php"
primeira_resposta = False  # Flag para resposta inicial no endpoint web

async def enviar_requisicao():
    global primeira_resposta
    try:
        logging.info("🚀 Iniciando nova solicitação ao servidor PHP...")

        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()

        # Abre a página e aguarda a rede ficar ociosa (JS resolvido)
        await page.goto(URL_SERVIDOR, {
            'timeout': 30000,
            'waitUntil': 'networkidle2'
        })

        await asyncio.sleep(3)  # espera extra para garantir execução de JS

        content = await page.content()
        await browser.close()

        # Extraindo texto limpo da página (opcional, pois pode conter HTML)
        text_lower = content.lower()

        logging.info(f"Resposta do PHP recebida (HTML): {content[:200]}...")  # Log parcial da resposta

        if "limite" in text_lower:
            logging.warning("🛑 Servidor PHP respondeu com 'limite'. Encerrando requisições.")
            return False  # para o loop

        logging.info("✅ Solicitação enviada com sucesso e resposta OK.")
        primeira_resposta = True
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

async def handle(request):
    if primeira_resposta:
        return web.Response(text="Render: Serviço ativo.")
    else:
        return web.Response(text="Render: Serviço ativo. Primeira solicitação enviada com sucesso.")

async def main():
    # Inicia loop de requisições em background
    asyncio.create_task(loop_continuo())

    # Configura servidor web para responder pings
    app = web.Application()
    app.router.add_get('/', handle)

    port = int(os.environ.get('PORT', 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    logging.info(f"🔵 Servidor web rodando em http://0.0.0.0:{port}")
    await site.start()

    # Mantém o serviço rodando
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.warning("🛑 Interrompido manualmente.")
    except Exception as e:
        logging.error(f"Erro fatal: {e}")
