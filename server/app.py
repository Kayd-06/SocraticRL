from openenv_core.env_server import create_fastapi_app
from server.environment import SocraticEnvironment
from models import SocraticAction, SocraticObservation

env = SocraticEnvironment()
app = create_fastapi_app(env, SocraticAction, SocraticObservation)
