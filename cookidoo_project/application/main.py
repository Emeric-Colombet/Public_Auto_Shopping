from cookidoo_project.domain.client import AuthenticationClient
from cookidoo_project.infrastructure.content_manager import FileManager
from cookidoo_project.infrastructure.Supermarket.carrefour import CarrefourInteract
from cookidoo_project.application import utils
import logging


config_dict = utils.read_safe_config_file()


authentication_client = AuthenticationClient(
    email=config_dict["username"],
    password=config_dict["password"],
    content_manager_static=FileManager,
)
client = authentication_client.generate_domain_client()
client.go_shopping()