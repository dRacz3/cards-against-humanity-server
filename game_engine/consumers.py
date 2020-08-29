import json
import time
from typing import Dict

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from cah_rules.GameSession import CAH_GameSession, CAH_GAME_SESSIONS
from cah_rules.models import Player


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.user_name = self.scope['url_route']['kwargs']['user_name']
        if self.room_name not in CAH_GAME_SESSIONS.keys():
            CAH_GAME_SESSIONS[self.room_name] = CAH_GameSession(f"{self.room_name}")
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await sync_to_async(CAH_GAME_SESSIONS[self.room_name].addNewUser)(self.user_name)
        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f"{self.user_name} has joined the game..."
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f"{self.user_name} has left the game..."
            }
        )

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if ('ls' in message):
            player_data = CAH_GAME_SESSIONS[self.room_name].session_player_data[self.user_name]
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': f"{player_data}"
                }
            )
        elif ('draw' in message):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': 'Drawing cards started...'
                }
            )
            await sync_to_async(CAH_GAME_SESSIONS[self.room_name].populatePlayerHandsWithCards)()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': 'Drawing cards has finished. Players will have their hands populated with cards'
                }
            )
        else:
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
