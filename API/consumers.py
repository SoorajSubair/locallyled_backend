import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Chat,Message,CustomUser


# class ChatConsumer(WebsocketConsumer):

#     def fetch_messages(self, data):
#         chat = Chat.objects.get(id = data['chatId'])
#         messages = Message.objects.filter(chat = chat)
#         content = {
#             'command': 'messages',
#             'messages': self.messages_to_json(messages)
#         }
#         self.send_message(content)
    
#     def new_message(self, data):
#         sender = CustomUser.objects.get(id = data['from'])
#         chat = Chat.objects.get(id = data['chatId'])
#         message = Message.objects.create(
#             chat = chat,
#             sender = sender,
#             content=data['message'])
#         content = {
#             'command': 'new_message',
#             'message': self.message_to_json(message)
#         }
#         return self.send_chat_message(content)


#     def messages_to_json(self, messages):
#         result = []
#         for message in messages:
#             result.append(self.message_to_json(message))
#         return result
    
#     def message_to_json(self, message):
#         return {
#             'id': message.id,
#             'sender': message.sender.first_name,
#             'senderId':message.sender.id,
#             'content': message.content,
#             'created_at': str(message.created_at)
#         }

#     commands = {
#         'fetch_messages': fetch_messages,
#         'new_message': new_message
#     }

#     def connect(self):
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#         self.room_group_name = "chat_%s" % self.room_name

#         # Join room group
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name, self.channel_name
#         )

#         self.accept()

#     def disconnect(self, close_code):
#         # Leave room group
#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_group_name, self.channel_name
#         )

#     # Receive message from WebSocket
#     def receive(self, text_data):
#         data = json.loads(text_data)
#         self.commands[data['command']](self, data)

#     def send_message(self, message):
#         self.send(text_data=json.dumps(message))

#     def send_chat_message(self, message):
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message
#             }
#         )

#     # Receive message from room group
#     def chat_message(self, event):
#         message = event["message"]

#         # Send message to WebSocket
#         self.send(text_data=json.dumps({"message": message}))


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        if data['command'] == 'new_message':
            sender = CustomUser.objects.get(id=data['from'])
            chat = Chat.objects.get(id=data['chatId'])
            message = Message.objects.create(
                chat=chat,
                sender=sender,
                content=data['message'])
            message_to_json = {
                'id': message.id,
                'sender': message.sender.first_name,
                'senderId': message.sender.id,
                'content': message.content,
                'created_at': str(message.created_at)
            }
            content = {
                'command': 'new_message',
                'message': message_to_json
            }

            # Send message to room group
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, {"type": "chat_message", "message": content}
            )

        if data['command'] == 'fetch_messages':
            chat = Chat.objects.get(id = data['chatId'])
            messages = Message.objects.filter(chat = chat)
            result = []
            for message in messages:
                message_to_json = {
                    'id': message.id,
                    'sender': message.sender.first_name,
                    'senderId': message.sender.id,
                    'content': message.content,
                    'created_at': str(message.created_at)
                }
                result.append(message_to_json)
            content = {
            'command': 'messages',
            'messages': result
            }

            self.send(text_data=json.dumps(content))
            



    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))