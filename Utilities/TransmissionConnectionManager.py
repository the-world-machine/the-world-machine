from typing import Union


class Connection:
    def __init__(self, server_id, channel_id):
        self.server_id = server_id
        self.channel_id = channel_id


class Transmission:
    def __init__(self, a: Connection, b: Union[Connection, None]):
        self.connection_a = a
        self.connection_b = b


transmissions: list[Transmission] = []


def create_connection(server_id, channel_id):
    connection = Connection(server_id, channel_id)
    transmissions.append(Transmission(connection, None))


def remove_connection(server_id):
    for t in transmissions:
        if t.connection_a.server_id == server_id:
            transmissions.remove(t)

        if t.connection_b.server_id == server_id:
            t.connection_b = None

def connect_to_transmission(server_id, channel_id):
    for t in transmissions:
        if t.connection_b is None:
            t.connection_b = Connection(server_id, channel_id)
            return


def get_transmission(server_id):
    for t in transmissions:
        if t.connection_a.server_id == server_id:
            return t

        if t.connection_b.server_id == server_id:
            return t


def connection_alive(server_id) -> bool:
    for t in transmissions:
        if t.connection_a.server_id == server_id:
            if t.connection_b is not None:
                return True
            return False

        if t.connection_b is not None:
            if t.connection_b.server_id == server_id:
                return True
            return False

    return False


def check_if_connected(server_id) -> bool:
    for t in transmissions:
        if t.connection_a.server_id == server_id:
            return True

        if t.connection_b is None:
            return False
        elif t.connection_b.server_id == server_id:
            return True

    return False
