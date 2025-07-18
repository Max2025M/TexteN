const puppeteer = require("puppeteer");

const URL_PHP = "https://livestream.ct.ws/M/receber.php";

// Aguarda X milissegundos
function esperar(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Loop principal
async function iniciarLoop() {
  let bloqueado = false;

  while (!bloqueado) {
    const browser = await puppeteer.launch({ headless: "new", args: ["--no-sandbox"] });
    const page = await browser.newPage();
    page.setDefaultNavigationTimeout(60000); // timeout de 60s

    try {
      console.log("🌐 Acessando:", URL_PHP);
      await page.goto(URL_PHP, { waitUntil: "networkidle2" });

      // Captura o conteúdo do body
      const resposta = await page.evaluate(() => document.body.innerText.trim());

      console.log("📩 Resposta do PHP:", resposta);

      if (resposta.toLowerCase().includes("limite")) {
        console.log("🛑 Limite atingido. Parando execução.");
        bloqueado = true;
      } else {
        console.log("⏳ Aguardando 10 segundos para nova solicitação...");
        await browser.close();
        await esperar(10000); // aguarda 10s
      }

    } catch (err) {
      console.error("❌ Erro ao acessar o PHP:", err.message);
    } finally {
      await browser.close();
    }
  }

  console.log("✅ Loop encerrado.");
}

// Inicia
iniciarLoop();
