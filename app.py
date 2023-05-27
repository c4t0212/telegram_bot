import uvicorn
import asyncio
from api import FastAPIApp
from dotenv import load_dotenv
from multiprocessing import Process
import telegram_bot


async def start_uvicorn(app):
    uvicorn_config = uvicorn.Config(app=app, host="0.0.0.0", port=8080, proxy_headers=True)
    server = uvicorn.Server(config=uvicorn_config)
    await server.serve()

def start_fastapi():
    load_dotenv('.env')
    bot = telegram_bot.bot
    api = FastAPIApp(bot)
    asyncio.run(start_uvicorn(api.app))

def start_bot():
    load_dotenv('.env')
    bot = telegram_bot.bot
    bot.run()

if __name__ == "__main__":    
    fastapi_process = Process(target=start_fastapi)
    bot_process = Process(target=start_bot)
    fastapi_process.start()
    bot_process.start()
    fastapi_process.join()
    bot_process.join()
