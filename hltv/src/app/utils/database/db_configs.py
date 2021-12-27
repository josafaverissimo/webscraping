from ..env.env import Env

# DEFAULT DB CONFIGS

env = Env()

default_config = {
    'host': 'localhost',
    'user': env.get_variable('DB_USER'),
    'password': env.get_variable('DB_PASSWD'),
    'db': 'hltv'
}
