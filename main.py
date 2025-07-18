import os
import asyncio
import logging
from aiohttp import web
from pyppeteer import launch
from pyppeteer.errors import TimeoutError

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')

URL_PHP = "https://livestream.ct.ws/M/receber.php"

async def enviar_requisicao_php():
    try:
        logging.info("🚀 Enviando requisição ao servidor PHP...")

        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()

        await page.goto(URL_PHP, {
            'timeout': 30000,
            'waitUntil': 'networkidle2'
        })

        await asyncio.sleep(3)  # garante execução JS

        conteudo = await page.evaluate('() => document.body.textContent')

        await browser.close()

        logging.info(f"📋 Resposta do PHP: {conteudo.strip()}")

        if "limite" in conteudo.lower():
            logging.warning("🛑 Limite atingido, parando as requisições ao PHP.")
            return False

        return True

    except TimeoutError:
        logging.error("⏰ Timeout ao acessar o PHP.")
        return True  # continuar tentando
    except Exception as e:
        logging.error(f"❌ Erro ao acessar o PHP: {e}")
        return True

async def loop_php():
    while True:
        continuar = await enviar_requisicao_php()
        if not continuar:
            break
        logging.info("⏳ Aguardando 60 segundos antes da próxima requisição PHP...")
        await asyncio.sleep(60)

async def handle(request):
    return web.Response(text="Render: Serviço ativo.")

async def main():
    # Start background task que roda as requisições ao PHP
    asyncio.create_task(loop_php())

    # Configura servidor web para o Render "ver que o serviço está online"
    app = web.Application()
    app.router.add_get('/', handle)

    port = int(os.environ.get('PORT', 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    logging.info(f"🔵 Servidor web rodando em http://0.0.0.0:{port}")
    await site.start()

    # Mantém o serviço rodando para o Render
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.warning("🛑 Interrompido manualmente.")
    except Exception as e:
        logging.error(f"Erro fatal: {e}")
