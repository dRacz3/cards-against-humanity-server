import json
import logging
from asgiref.sync import sync_to_async, async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from cah_rules.GameSession import CAH_GameSession, CAH_GAME_SESSIONS, GameEvents
from common.IEventDispatcher import IEventDispatcher


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
        self.user_name = self.scope['url_route']['kwargs']['user_name']
        self.logger = logging.getLogger(self.room_name)
        self.room_group_name = 'chat_%s' % self.room_name
        self.eventDispatcher = CAHGameEventDispatcher(self.channel_layer, self.room_name)

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        if self.room_name not in CAH_GAME_SESSIONS.keys():
            self.logger.info(f"Creating session for room name: {self.room_name}")
            CAH_GAME_SESSIONS[self.room_name] = CAH_GameSession(f"{self.room_name}",
                                                                self.eventDispatcher.asyncGameEventDispatcher)
        failed_to_add = await sync_to_async(CAH_GAME_SESSIONS[self.room_name].addNewUser)(self.user_name)
        if not failed_to_add:
            await self.accept()

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_event',
                    'event_name': GameEvents.PLAYER_CONNECTED.name,
                    'message': f"Added new player: {self.user_name}"
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
        self.logger.info(f"Received: {text_data_json}")
        try:
            message = text_data_json['message']
            if (self.AcceptedCommands.LS in message):
                await self.list_players()
            if (self.AcceptedCommands.STATUS in message):
                await self.broadcast_to_group(str(CAH_GAME_SESSIONS[self.room_name]))
            elif (self.AcceptedCommands.DRAW in message):
                await self.draw_cards_for_everyone()
            elif (self.AcceptedCommands.START in message):
                await sync_to_async(CAH_GAME_SESSIONS[self.room_name].startGame)()
            elif (self.AcceptedCommands.SUBMIT in message):
                self.logger.info(f"Submission: {message}")
                start_index = message.find(self.AcceptedCommands.SUBMIT) + len(self.AcceptedCommands.SUBMIT) + 1
                card_content = message[start_index:]
                cards = card_content.split('|')
                self.logger.info(f"Cards texts {cards}")
                await sync_to_async(CAH_GAME_SESSIONS[self.room_name].submit_user_card)(self.user_name, cards)
            elif (self.AcceptedCommands.END_ROUND in message):
                self.logger.info("Ending round...")
                await sync_to_async(CAH_GAME_SESSIONS[self.room_name].endRound)()
            elif (self.AcceptedCommands.SELECT_WINNER in message):
                start_index = message.find(self.AcceptedCommands.SELECT_WINNER) + len(
                    self.AcceptedCommands.SELECT_WINNER) + 1
                winner_name = message[start_index:]
                self.logger.info(f"Selecting winner.. winner is: {winner_name}")
                await sync_to_async(CAH_GAME_SESSIONS[self.room_name].selectWinner)(winner_name)
            else:
                await self.broadcast_to_group(message)
        except Exception as e:
            self.logger.info(f"Error! {e}")
            await self.broadcast_to_group(f"Error! + {e}")

    async def broadcast_to_group(self, message: str, type='chat_message'):
        print(f"Broadcasting message: {message}")
        await self.channel_layer.group_send(
            self.room_group_name,
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

    async def game_event(self, event):
        message = event['message']
        event_name = event["event_name"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'event_name': event_name,
            'message': message
        }))


class CAHGameEventDispatcher:
    def __init__(self, channel_layer, room_name: str):
        self.asyncGameEventDispatcher = AsyncGameEventDispatcher(channel_layer, room_name)
        self.events = GameEvents

    def broadcast_status(self, status):
        self.asyncGameEventDispatcher.emit(status, event_name=self.events.STATUS_BROADCAST.name)


class AsyncGameEventDispatcher(IEventDispatcher):
    def __init__(self, channel_layer: str, room_name: str):
        super().__init__()
        self.channel_layer = channel_layer
        self.room_group_name = room_name
        self.logger = None

    def setLogger(self, logger):
        self.logger = logger

    def emit(self, message, event_name):
        if self.logger is not None:
            self.logger.info(f"[{event_name}][{message}]")
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'game_event',
                'event_name': event_name,
                'message': message
            }
        )
