from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth.models import AnonymousUser
from courses.models import Batch
from channels.db import database_sync_to_async
from django.core.cache import cache

class ClassRoomConsumer(AsyncWebsocketConsumer):
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
                if cache.get(f"opened_class_data:{batch_name}"):
                    print('Class already opened. Disconnecting...')
                    await self.send(text_data=json.dumps({'message': 'Class already opened. Disconnecting...'}))
                    await self.close()
                    return
                cache.set(f"opened_class_data:{batch_name}", json.dumps([user_email, self.channel_name]), timeout=14400)
                self.admin = True
                await self.channel_layer.group_add(self.batch_name,self.channel_name)
                await self.send(text_data=json.dumps({'message': f'Class room opened.'}))
                return
            else:
                print('student fount to join the class...' )
                active_students_list = json.loads(cache.get("active_students_list", "[]"))
                if user_email  in active_students_list:
                    print('duplicate student found...')
                    await self.send(text_data=json.dumps({'message': 'Duplicate student'}))
                    active_students_list.append(user_email)
                    cache.set("active_students_list", json.dumps(active_students_list))
                    await self.close()
                    return
                if not cache.get(f"opened_class_data:{batch_name}"):
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
                instructor_channel_name = json.loads(cache.get(f"opened_class_data:{batch_name}"))[1]
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
            student_email = recieved_data['student_email']
            student_channel_name = recieved_data['student_channel_name']
            data = {'message': 'Permission granted to join class'}
            await self.channel_layer.send(
                student_channel_name,
                {
                    'type': 'send.msg',
                    'data': data
                }
            )
            active_students_list = json.loads(cache.get("active_students_list", "[]"))
            active_students_list.append(student_email)
            cache.set("active_students_list", json.dumps(active_students_list))
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
        if action == 'student-removed':
            print('inside student-removed...')
            student_channel_name = recieved_data.pop('student_channel_name')
            await self.channel_layer.send(
                student_channel_name,
                {
                    'type': 'student.removed',
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
            cache.delete(f"opened_class_data:{self.batch_name}")
            print(f'batch- {self.batch_name} removed from cache - ')
            return
        else:
            print('student disconnect called...')
            email = self.email
            data = {
                    'user': email,
                    'action': 'student-close',
                }
            active_students_list = json.loads(cache.get("active_students_list", "[]"))
            instructor_channel_name = None
            if cache.get(f"opened_class_data:{self.batch_name}"):
                instructor_channel_name = json.loads(cache.get(f"opened_class_data:{self.batch_name}"))[1]
            if  active_students_list.count(email) == 1:
                if instructor_channel_name:
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
            if email in active_students_list:
                active_students_list.remove(email)
                cache.set("active_students_list", json.dumps(active_students_list))
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

    async def student_removed(self, event):
        print('student_removed called...')
        data = event['data']
        await self.send(text_data=json.dumps(data))
        print('student-removed action sent to student.')
        await self.close()

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
    