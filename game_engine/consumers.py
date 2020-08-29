import json
import logging
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from cah_rules.GameSession import CAH_GameSession, CAH_GAME_SESSIONS


class ChatConsumer(AsyncWebsocketConsumer):
    class AcceptedCommands:
        LS = 'ls'
        START = 'start'
        DRAW = 'draw'
        SUBMIT = '__submit__'

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.user_name = self.scope['url_route']['kwargs']['user_name']
        self.logger = logging.getLogger(self.room_name)
        if self.room_name not in CAH_GAME_SESSIONS.keys():
            self.logger.info(f"Creating session for room name: {self.room_name}")
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
        self.logger.warning(f"{self.user_name} has disconnected... removing from game")
        CAH_GAME_SESSIONS[self.room_name].removeUser(self.user_name)
        if (CAH_GAME_SESSIONS[self.room_name].get_currently_active_player_count()) == 0:
            self.logger.info("No more players left in the room, removing session to save some space")
            del CAH_GAME_SESSIONS[self.room_name]
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

        if (self.AcceptedCommands.LS in message):
            await self.list_players()
        elif (self.AcceptedCommands.DRAW in message):
            await self.draw_cards_for_everyone()
        elif(self.AcceptedCommands.START in message):
            await sync_to_async(CAH_GAME_SESSIONS[self.room_name].startGame)()
        elif(self.AcceptedCommands.SUBMIT in message):
            self.logger.info(f"Submission: {message}")
            start_index = message.find(self.AcceptedCommands.SUBMIT) + len(self.AcceptedCommands.SUBMIT) + 1
            card_content = message[start_index:]
            cards = card_content.split('|')
            self.logger.info(f"Cards texts {cards}")
            await sync_to_async(CAH_GAME_SESSIONS[self.room_name].submit_user_card)(self.user_name, cards)
        else:
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message
                }
            )

    async def draw_cards_for_everyone(self):
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

    async def list_players(self):
        player_data = CAH_GAME_SESSIONS[self.room_name].session_player_data
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f"{player_data}"
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
