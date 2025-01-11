from entities.model import TRivalCouple
from helper.message_type import MessageType
from websocket.connection_manager import ConnectionManager


async def notify_enemy_about_game_creation(rc: TRivalCouple, manager: ConnectionManager):
    await manager.send_structured_data(rc.dfplayer1, MessageType.GAME_CREATION.value,
                                       {'enemy_nickname': rc.dfplayer2_nickname, 'gameId': str(rc.id)})
    await manager.send_structured_data(rc.dfplayer2, MessageType.GAME_CREATION.value,
                                       {'enemy_nickname': rc.dfplayer1_nickname, 'gameId': str(rc.id)})