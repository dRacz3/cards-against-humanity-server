import json
import logging
from asgiref.sync import sync_to_async, async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.authtoken.models import Token
from channels.auth import login

from cah_rules.GameSession import CAH_GameSession, CAH_GAME_SESSIONS, GameEvents
from common.IEventDispatcher import IEventDispatcher
from game_engine.models import GameSession, Profile

from cah_rules.GameManager import CAHGameManager, UPDATE_COMMANDS


class ChatConsumer(AsyncWebsocketConsumer):
    class AcceptedCommands:
        LS = 'ls'
        START = 'start'
        DRAW = 'draw'
        STATUS = '__status__'
        SUBMIT = '__submit__'
        END_ROUND = '__endround__'
        SELECT_WINNER = '__selectwinner__'

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.logger = logging.getLogger(self.room_name)

        def get_user_by_token(token_key):
            try:
                token = Token.objects.get(key=token_key[1])
                return token.user
            except Exception as e:
                return

        user = await sync_to_async(get_user_by_token)(self.scope['query_string'].decode().split('='))
        try:
            await sync_to_async(login)(self.scope, user)
            self.user = user
        except Exception as e:
            self.logger.warning("Failed to authenticate user")

        user_add_success = await sync_to_async(CAHGameManager.add_user_to_session)(self.room_name, self.scope["user"])

        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        if user_add_success:
            message = f"Player connected to room: {self.user}"
        else:
            message = "Failed to add user to session... Not authenticated"
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_event',
                'event_name': GameEvents.PLAYER_CONNECTED.name,
                'message': message
            }
        )
        await self.broadcast_to_group(f"{UPDATE_COMMANDS.UPDATE}")

    async def disconnect(self, close_code):
        self.logger.warning(f"{self.user} has disconnected... removing from game")
        await sync_to_async(CAHGameManager.remove_user_from_session)(self.room_name, self.scope['user'])
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f"{self.user} has left the game..."
            }
        )

        await self.broadcast_to_group(f"{UPDATE_COMMANDS.UPDATE}")

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def broadcast_to_group(self, message: str, type='chat_message'):
        print(f"Broadcasting message: {message}")
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': type,
                'message': message
            }
        )

    async def send_to_single_user(self, message: str, type='chat_message'):
        print(f"Broadcasting message: {message} to channel: {self.channel_name}")
        await self.channel_layer.send(
            self.channel_name,
            {
                'type': type,
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

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        self.logger.info(f"Received: {text_data_json}")
        try:
            message = text_data_json['message']
            print(f"Processing: {message}")
            if ('step' in message):
                result = await sync_to_async(CAHGameManager.progress_game)(self.room_name)
                await self.broadcast_to_group(f"{result}")
            elif (self.AcceptedCommands.SUBMIT in message):
                self.logger.info(f"Submission: {message}")
                submitted_card_pks = message.split('|')[1:]
                print(f"Submitted card pks: {submitted_card_pks}")
                result = await sync_to_async(CAHGameManager.submit_cards)(self.room_name, self.scope["user"],
                                                                          submitted_card_pks)
                await self.broadcast_to_group(f"{result}")
            elif (self.AcceptedCommands.SELECT_WINNER in message):
                start_index = message.find(self.AcceptedCommands.SELECT_WINNER) + len(
                    self.AcceptedCommands.SELECT_WINNER) + 1
                winning_submission = message[start_index:]
                self.logger.info(f"Selecting winner.. winner is submission with id: {winning_submission}")
                winner = await sync_to_async(CAHGameManager.select_winner)(winning_submission, self.room_name)
                await self.broadcast_to_group(f"__DECLARE_WINNER__|{winner}")
            else:
                await self.broadcast_to_group(message)
        except Exception as e:
            self.logger.info(f"Error! {e}")
            await self.send_to_single_user(f"Error! + {e}")

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def game_event(self, event):
        message = event['message']
        event_name = event["event_name"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'event_name': event_name,
            'message': message
        }))
