from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ClassRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('inside connect consumer')
        self.room_group_name = 'Class-Room'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print('Connection accepted')
    
    async def disconnect(self, code):
        print('inside disconnect')
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print('User Disconnected.')


    async def receive(self, text_data=None):
        print('inside recieve')
        recieved_dict = json.loads(text_data)
        message = recieved_dict('message')

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                type: 'send.message',
                'message': message
            }
        )

    async def send_message(self, event):
        print('inside send sdp')
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))
    