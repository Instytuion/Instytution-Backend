from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ClassRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('inside connect consumer')
        print('user scope -', self.scope["user"])
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
        action = recieved_dict['action']

        if (action == 'new-offer') or (action == 'new-answer'):
            receiver_channel_name = recieved_dict['message']['receiver_channel_name']
            recieved_dict['message']['receiver_channel_name'] = self.channel_name
            await self.channel_layer.send(
                receiver_channel_name,
                {
                    'type': 'send.sdp',
                    'recieved_dict': recieved_dict
                }
            )
            return

        recieved_dict['message']['receiver_channel_name'] = self.channel_name
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send.sdp',
                'recieved_dict': recieved_dict
            }
        )

    async def send_sdp(self, event):
        print('inside send sdp')
        recieved_dict = event['recieved_dict']

        await self.send(text_data=json.dumps(recieved_dict))
    