from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth.models import AnonymousUser
from courses.models import Batch
from channels.db import database_sync_to_async

class ClassRoomConsumer(AsyncWebsocketConsumer):
    # This 'opened_class_data' will hold neccessary data needed track an opened class.
    opened_class_data = dict()
    async def connect(self):
        print('inside connect consumer')
        subprotocols = self.scope.get('subprotocols', [])
        url_batch_name = self.scope['url_route']['kwargs']['batch_name']
        batch_name = url_batch_name.replace(' ', '-') # Format to set as channel group name        
        self.admin = False
        self.batch_name = batch_name
        print("batch name is -", batch_name)
        if isinstance(self.scope['user'], AnonymousUser):
            await self.accept(subprotocol='jwt')
            await self.send(text_data=json.dumps({'message': f'Unautherized Entry. Try again'}))
            await self.close()
            return
        
        # Store user info for later use
        user = self.scope['user']
        self.role = user.role
        self.email = user.email

        if 'jwt' in subprotocols:
            await self.accept(subprotocol='jwt')
            print('Connection accepted')
            try:
                batch_instructor_email = await self.get_batch_instructor_email(url_batch_name)
            except Batch.DoesNotExist:
                await self.send(text_data=json.dumps({'message': 'Batch not found. Disconnecting...'}))
                await self.close()
                return
            user_email = user.email
            if user_email == batch_instructor_email:
                print('instructor as admin found to open class room...' )
                if batch_name in ClassRoomConsumer.opened_class_data:
                    print('Class already opened. Disconnecting...')
                    await self.send(text_data=json.dumps({'message': 'Class already opened. Disconnecting...'}))
                    await self.close()
                    return
                ClassRoomConsumer.opened_class_data[batch_name] = [user_email, self.channel_name]
                self.admin = True
                await self.channel_layer.group_add(self.batch_name,self.channel_name)
                await self.send(text_data=json.dumps({'message': f'Class room opened.'}))
                return
            else:
                print('student fount to join the class...' )
                if batch_name not in ClassRoomConsumer.opened_class_data:
                    print('No room condition called...')
                    await self.send(text_data=json.dumps({'message': f'Class room not opened yet. Disconnecting...'}))
                    await self.close()
                    return
                await self.channel_layer.group_add(self.batch_name,self.channel_name)
                await self.send(text_data=json.dumps({'message': f'Waiting for permission.'}))
                data = {
                    'user': user.email,
                    'action': 'new-peer',
                    'student_channel_name': self.channel_name
                }
                instructor_channel_name = ClassRoomConsumer.opened_class_data[self.batch_name][1]
                await self.channel_layer.send(
                    instructor_channel_name,
                    {
                        'type': 'student.request',
                        'data': data
                    }
                )
                return
        else:
            print('Unsupported subprotocol, closing connection.')
            await self.close() 

    async def receive(self, text_data=None):
        print('inside recieve')
        recieved_data = json.loads(text_data)
        message = recieved_data.get('message')
        action = recieved_data.get('action')

        if message == 'student_allowed':
            print('message_allowed is true')
            student_channel_name = recieved_data['student_channel_name']
            data = {'message': 'Permission granted to join class'}
            await self.channel_layer.send(
                student_channel_name,
                {
                    'type': 'send.msg',
                    'data': data
                }
            )
            return

        if message == 'student_dissallowed':
            print('message_dissallowed is true')
            student_channel_name = recieved_data['student_channel_name']
            data = {'message': 'Permission denied to join class'}
            await self.channel_layer.send(
                student_channel_name,
                {
                    'type': 'send.msg',
                    'data': data
                }
            )
            return
        if action == 'new-offer':
            print('inside new-offer...')
            student_channel_name = recieved_data.pop('student_channel_name')
            recieved_data['instructor_channel_name'] = self.channel_name
            await self.channel_layer.send(
                student_channel_name,
                {
                    'type': 'send.sdp',
                    'data': recieved_data
                }
            )
            return
        if action == 'new-answer':
            print('inside new-answer...')
            instructor_channel_name = recieved_data.pop('instructor_channel_name')
            recieved_data['student_channel_name'] = self.channel_name
            await self.channel_layer.send(
                instructor_channel_name,
                {
                    'type': 'send.sdp',
                    'data': recieved_data
                }
            )
            return
        if action == 'ice-candidate':
            print('inside new ice-candidate...')
            receiver_channel_name = recieved_data.pop('receiver_channel_name')
            await self.channel_layer.send(
                receiver_channel_name,
                {
                    'type': 'send.candidate',
                    'data': recieved_data
                }
            )
            return

    
    async def disconnect(self, code):
        print('inside disconnect')
        if self.admin:
            print('class admin disconnect called...')
            data = {'message': "class clossed"}
            await self.channel_layer.group_send(
                self.batch_name,
                {
                    'type': 'close.class',
                    'data': data
                }
            )
            await self.channel_layer.group_discard(self.batch_name,self.channel_name)
            if self.batch_name in ClassRoomConsumer.opened_class_data:
                del ClassRoomConsumer.opened_class_data[self.batch_name]
                print('batch removed from open class dict - ', ClassRoomConsumer.opened_class_data)
            return
        else:
            print('student disconnect called...')
            data = {
                    'user': self.email,
                    'action': 'student-close',
                }
            instructor_channel_name = ClassRoomConsumer.opened_class_data[self.batch_name][1]
            await self.channel_layer.send(
                instructor_channel_name,
                {
                    'type': 'student.close',
                    'data': data
                }
            )
            await self.channel_layer.group_discard(
                self.batch_name,
                self.channel_name
            )
            return

    async def student_request(self, event):
        print('student_request called...')
        data = event['data']
        print('new peer sent to admin instructor...')
        await self.send(text_data=json.dumps(data))

    async def send_msg(self, event):
        print('send_msg called...')
        data = event['data']
        await self.send(text_data=json.dumps(data))

    async def close_class(self, event):
        print('close_class called...')
        data = event['data']
        if not self.admin:
            await self.send(text_data=json.dumps(data))
            await self.close()

    async def student_close(self, event):
        print('student_close called...')
        data = event['data']
        await self.send(text_data=json.dumps(data))
        print('student close action sent to instructor')

    async def send_sdp(self, event):
        print('inside send sdp')
        data = event['data']
        await self.send(text_data=json.dumps(data))

    async def send_candidate(self, event):
        print('inside send candidate')
        data = event['data']
        await self.send(text_data=json.dumps(data))

    @database_sync_to_async
    def get_batch_instructor_email(self, url_batch_name):
        batch = Batch.objects.select_related('instructor').get(name=url_batch_name)
        return batch.instructor.email
    