import asyncio
import os
from pyppeteer import launch

URL_PHP = "https://livestream.ct.ws/M/receber.php"
ARQUIVO_DESBLOQUEIO = "desbloqueado.txt"

async def esperar(ms):
    await asyncio.sleep(ms / 1000)

async def desbloqueado():
    return os.path.exists(ARQUIVO_DESBLOQUEIO)

async def iniciar_loop():
    bloqueado = False

    while True:
        browser = await launch(headless=True, args=['--no-sandbox'])
        page = await browser.newPage()
        page.setDefaultNavigationTimeout(60000)

        try:
            print(f"🌐 Acessando: {URL_PHP}")
            response = await page.goto(URL_PHP, waitUntil='networkidle2')
            resposta = await page.evaluate('document.body.innerText')
            resposta = resposta.strip()
            print(f"📩 Resposta do PHP: {resposta}")

            if 'limite' in resposta.lower():
                print("🛑 Limite atingido. Aguardando desbloqueio externo...")

                bloqueado = True
                await browser.close()

                # Espera desbloqueio externo via arquivo
                while bloqueado:
                    if await desbloqueado():
                        print("✅ Desbloqueio detectado! Removendo flag...")
                        os.remove(ARQUIVO_DESBLOQUEIO)
                        bloqueado = False
                        break
                    await esperar(3000)

            else:
                print("⏳ Esperando 10 segundos antes da próxima solicitação...")
                await browser.close()
                await esperar(10000)

        except Exception as e:
            print(f"❌ Erro: {e}")
            await browser.close()

if __name__ == "__main__":
    asyncio.run(iniciar_loop())
