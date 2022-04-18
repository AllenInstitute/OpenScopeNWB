from openscopenwb.utils import postgres_functions as postgres


def get_path(session_id):
    path = postgres.get_sess_directory(session_id)
    return path

