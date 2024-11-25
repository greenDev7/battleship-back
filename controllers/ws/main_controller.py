import uuid
from fastapi import WebSocket

from controllers.ws.user import create_active_user, get_active_user_nick_name_for_random_game


async def process_data(client_uuid: uuid.UUID, data_from_client: dict, ws: WebSocket) -> dict:

    msg_type = data_from_client['msg_type']

    if msg_type == 'active_user_for_random_game_creation':
        try:
            create_active_user(client_uuid, data_from_client, ws.client.host, ws.client.port)
            nick_name = get_active_user_nick_name_for_random_game(client_uuid)
            return {'msg_type': msg_type, 'data': nick_name, 'status': 'ok'}
        except Exception as ex:
            return {'msg_type': msg_type, 'data': str(ex), 'status': 'error'}

