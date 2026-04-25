from openenv_core.env_server import create_fastapi_app
from server.environment import SocraticEnvironment
from models import SocraticAction, SocraticObservation

app = create_fastapi_app(SocraticEnvironment, SocraticAction, SocraticObservation)
