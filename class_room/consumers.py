from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth.models import AnonymousUser

class ClassRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('inside connect consumer')
        subprotocols = self.scope.get('subprotocols', [])
        url_batch_name = self.scope['url_route']['kwargs']['batch_name']
        batch_name = url_batch_name.replace(' ', '-')
        print("batch name is -", batch_name)
        if isinstance(self.scope['user'], AnonymousUser):
            await self.accept(subprotocol='jwt')
            await self.send(text_data=json.dumps({'message_error': f'Unautherized Entry. Try again'}))
            await self.close()
            return
        user = self.scope['user']
        # Store user role for later use
        self.role = user.role
        if 'jwt' in subprotocols:
            await self.accept(subprotocol='jwt')
            print('Connection accepted')
            self.room_group_name = f"Class-room-{batch_name}"
            if  self.role == 'instructor':
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                
                await self.send(text_data=json.dumps({'message': f'{self.room_group_name} opened.'}))
            else:
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                data = {
                    'user': user.email,
                    'action': 'new-peer',
                    'student_channel_name': self.channel_name
                }
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'student.request',
                        'data': data
                    }
                )

        else:
            print('Unsupported subprotocol, closing connection.')
            await self.close() 

    
    async def disconnect(self, code):
        print('inside disconnect')
        # await self.channel_layer.group_discard(
        #     self.room_group_name,
        #     self.channel_name
        # )
        print('User Disconnected.')

    async def student_request(self, event):
        print("student_request called")
        data = event['data']
        
        if self.role == 'instructor':
            await self.send(text_data=json.dumps(data))



    # async def receive(self, text_data=None):
    #     print('inside recieve')
    #     recieved_dict = json.loads(text_data)
    #     action = recieved_dict['action']

    #     if (action == 'new-offer') or (action == 'new-answer'):
    #         receiver_channel_name = recieved_dict['message']['receiver_channel_name']
    #         recieved_dict['message']['receiver_channel_name'] = self.channel_name
    #         await self.channel_layer.send(
    #             receiver_channel_name,
    #             {
    #                 'type': 'send.sdp',
    #                 'recieved_dict': recieved_dict
    #             }
    #         )
    #         return

    #     recieved_dict['message']['receiver_channel_name'] = self.channel_name
    #     await self.channel_layer.group_send(
    #         self.room_group_name,
    #         {
    #             'type': 'send.sdp',
    #             'recieved_dict': recieved_dict
    #         }
    #     )

    # async def send_sdp(self, event):
    #     print('inside send sdp')
    #     recieved_dict = event['recieved_dict']

    #     await self.send(text_data=json.dumps(recieved_dict))
    