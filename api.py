import database
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
import base64
import io

class Item(BaseModel):
    message: str
    status: Optional[str] = None
    image: Optional[str] = None

class FastAPIApp:
    def check_base64(self, image) -> bool:
        try:
            base64.b64decode(image)
            return True
        except Exception as e:
            return False
        
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
                if self.check_base64(item.image):
                    image = io.BytesIO(base64.b64decode(item.image))
                    await self.bot.app.bot.send_photo(chat_id=chat_id, photo=image)
                    print('Image sent')
                    # await self.bot.app.bot.send_photo(chat_id=chat_id, photo=base64.b64decode(item.image))
            return {'message': 'Notification sent successfully'}
