import asyncio
import os
import uvicorn
from fastapi import FastAPI
from pyppeteer import launch

URL_PHP = "https://livestream.ct.ws/M/receber.php"

app = FastAPI()

loop_task = None
parar = False  # flag para controlar parada do loop

async def esperar(ms):
    await asyncio.sleep(ms / 1000)

async def executar_loop():
    global parar
    while not parar:
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
                print("🛑 Limite atingido. Parando envio de solicitações.")
                parar = True
                await browser.close()
                break

            print("⏳ Esperando 10 segundos antes da próxima solicitação...")
            await browser.close()
            await esperar(10000)

        except Exception as e:
            print(f"❌ Erro: {e}")
            await browser.close()

@app.on_event("startup")
async def startup_event():
    global loop_task
    print("🚀 Iniciando loop assíncrono de solicitações...")
    loop_task = asyncio.create_task(executar_loop())

@app.get("/")
async def raiz():
    return {"status": "Rodando"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
