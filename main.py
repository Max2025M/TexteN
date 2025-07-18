import asyncio
import os
from fastapi import FastAPI
from pyppeteer import launch
import uvicorn

URL_PHP = "https://livestream.ct.ws/M/receber.php"

app = FastAPI()

loop_task = None
parar = False
loop_rodando = False

async def esperar(ms):
    await asyncio.sleep(ms / 1000)

async def executar_loop():
    global parar, loop_rodando
    loop_rodando = True
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

    loop_rodando = False

@app.get("/")
async def raiz():
    return {"status": "Rodando", "loop_ativo": not parar}

@app.get("/loop")
async def reativar_loop():
    global loop_task, parar
    if parar or not loop_rodando:
        print("🔁 Reativando loop de solicitações...")
        parar = False
        loop_task = asyncio.create_task(executar_loop())
        return {"status": "Loop reiniciado"}
    else:
        return {"status": "Loop já está em execução"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
