import database
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    message: str
    status: Optional[str] = None

class FastAPIApp:
    def __init__(self, bot) -> None:
        self.app = FastAPI()
        self.bot = bot
        self.db = database.db
        @self.app.post('/v1/notify')
        async def notify(item: Item):
            message = item.message
            status = item.status
            db_name = 'notify'
            mango_query = {
                "selector": {
                    "message": message
                },
                "fields": [
                    'chat_id'
                ]
            }
            subscribers = list(self.db[db_name].find(mango_query))
            if len(subscribers) == 0:
                return {'message': 'No subscribers'}
            subscribers = subscribers[0]['chat_id']
            for chat_id in subscribers:
                text = f'Message: {message}\nStatus: {status}'
                await self.bot.app.bot.send_message(chat_id=chat_id, text=text)
            return {'message': 'Notification sent successfully'}
