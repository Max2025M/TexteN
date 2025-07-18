import os
import asyncio
import logging
from aiohttp import web
from pyppeteer import launch
from pyppeteer.errors import TimeoutError

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')

URL_PHP = "https://livestream.ct.ws/M/receber.php"
bloqueado = False  # flag global para controle de pausa/executar

async def enviar_requisicao_php():
    global bloqueado
    try:
        if bloqueado:
            logging.warning("🚫 Execução pausada por bloqueio ('limite'). Aguardando desbloqueio via /desbloquear.")
            await asyncio.sleep(10)
            return True

        logging.info("🚀 Enviando requisição ao servidor PHP...")

        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()

        await page.goto(URL_PHP, {
            'timeout': 30000,
            'waitUntil': 'networkidle2'
        })

        await asyncio.sleep(3)  # Garante execução de scripts JS

        conteudo = await page.evaluate('() => document.body.textContent')
        await browser.close()

        conteudo = conteudo.strip()
        logging.info(f"📋 Resposta recebida: {conteudo}")

        if "limite" in conteudo.lower():
            logging.warning("🛑 Limite detectado! Travando execuções até desbloqueio...")
            bloqueado = True
            return True

        if "sucesso" in conteudo.lower():
            logging.info("✅ Sucesso detectado. Aguardando 10 segundos para próxima requisição...")
            await asyncio.sleep(10)
            return True

        logging.info("ℹ️ Resposta sem sucesso. Aguardando 10 segundos antes de tentar novamente...")
        await asyncio.sleep(10)
        return True

    except TimeoutError:
        logging.error("⏰ Timeout ao acessar o PHP. Tentando novamente em 10 segundos...")
        await asyncio.sleep(10)
        return True
    except Exception as e:
        logging.error(f"❌ Erro ao acessar o PHP: {e}. Tentando novamente em 10 segundos...")
        await asyncio.sleep(10)
        return True

async def loop_php():
    while True:
        continuar = await enviar_requisicao_php()
        if not continuar:
            break

async def handle(request):
    return web.Response(text="Render: Serviço ativo.")

async def desbloquear(request):
    global bloqueado
    try:
        dados = await request.json()
        if dados.get("acao") == "remover_limite":
            bloqueado = False
            logging.info("🔓 Desbloqueio recebido via POST. Retomando execuções.")
            return web.json_response({"status": "sucesso", "mensagem": "limite removido"})
        else:
            return web.json_response({"status": "erro", "mensagem": "ação inválida"}, status=400)
    except Exception as e:
        logging.error(f"❌ Erro no desbloqueio: {e}")
        return web.json_response({"status": "erro", "mensagem": str(e)}, status=500)

async def status(request):
    global bloqueado
    status_atual = "bloqueado" if bloqueado else "ativo"
    return web.json_response({"status": status_atual})

async def main():
    # Inicia tarefa que faz requisições ao PHP em loop
    asyncio.create_task(loop_php())

    # Configura servidor web para aceitar requisições HTTP
    app = web.Application()
    app.router.add_get('/', handle)
    app.router.add_post('/desbloquear', desbloquear)
    app.router.add_get('/status', status)  # rota status para consulta do estado atual

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
