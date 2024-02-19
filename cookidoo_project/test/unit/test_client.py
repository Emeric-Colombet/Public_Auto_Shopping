import pytest
from cookidoo_project.domain.client import AuthenticationClient, Client
from cookidoo_project.infrastructure.Supermarket.carrefour import CarrefourInteract
from cookidoo_project.infrastructure.Shopping_list.cookidoo import CookidooInteract
from cookidoo_project.infrastructure.content_manager import FileManager
from cookidoo_project.infrastructure.Shopping_list.cookidoo import CookidooInteract
from cookidoo_project.application import utils
import pandas as pd
import os
from time import sleep

data_raw_shopping_list = {
    "raw_data_shopping_list" : [
        "125 g de riz long",
        "3 c. à café d'épices gyros",
        "1 c. à café d'origan déshydraté"
        ]
    }
ingredients_to_order = ['riz long de camargue complet etuve igp reflets de france', 'epices ras el hanout ducros', 'Not found']


class TestClientFileImplementation():
    """Testing client with file implementation."""
        
    @pytest.mark.usefixtures("generate_multiple_client_authentified")
    def test_create_domain_client(self,generate_multiple_client_authentified,monkeypatch):
        temp_dir, authentication_filename = generate_multiple_client_authentified
        """
            GIVEN a monkeypatched version of CarrefourInteract
            WHEN Client() is called
            THEN doesn't initiate the post_init_ connection.
        """
        def mock_post_init(self):
            return None
        def return_none():
            return None
        monkeypatch.setattr(CarrefourInteract,'__post_init__',mock_post_init)
        monkeypatch.setattr(CookidooInteract,'__post_init__',mock_post_init)
        monkeypatch.setattr(utils,'generate_chrome_driver',return_none)
        monkeypatch.setattr(FileManager.authenticate,'__defaults__',(authentication_filename,))
        authentication_client = AuthenticationClient(email="emeric.colombet@gmail.com",password="PASSWORD",content_manager_static=FileManager)
        client = authentication_client.generate_domain_client()
        assert isinstance(client,Client)
        
    
    @pytest.mark.usefixtures("generate_authentified_client_with_empty_structure")
    def test_customer_retrieve_history_and_store_it(self, generate_authentified_client_with_empty_structure,monkeypatch):
        temp_dir = generate_authentified_client_with_empty_structure
        authentication_filename = os.path.join(temp_dir,"Auth.csv")
        def mock_post_init(self):
            return None
        def mock_shopping_list_retreive_history(self):
            return pd.DataFrame(data=data_raw_shopping_list)
        def return_none():
                return None
        monkeypatch.setattr(CarrefourInteract,'__post_init__',mock_post_init)
        monkeypatch.setattr(CookidooInteract,'__post_init__',mock_post_init)
        monkeypatch.setattr(CookidooInteract,'retrieve_shopping_list',mock_shopping_list_retreive_history)
        monkeypatch.setattr(utils,'generate_chrome_driver',return_none)
        monkeypatch.setattr(FileManager.authenticate,'__defaults__',(authentication_filename,))
        
        authentication_client = AuthenticationClient(email="emeric.colombet@gmail.com",password="PASSWORD",content_manager_static=FileManager,shopping_path=temp_dir)
        client = authentication_client.generate_domain_client()
        shopping_list = client.retrieve_shopping_list()
        # The following test assert that the raw_shopping_list was correctly mocked, and stored with an authentified client. 
        pd.testing.assert_frame_equal(client.content_manager.load_raw_shopping_list(shopping_list_name=utils.get_date_with_underscore()),shopping_list)

    @pytest.mark.usefixtures("generate_drive_history_order_with_empty_structure")
    def test_customer_authentication_then_loading_history_then_load_model_then_match_ingredients(
        self,
        generate_drive_history_order_with_empty_structure,
        monkeypatch):
        temp_dir = generate_drive_history_order_with_empty_structure
        authentication_filename = os.path.join(temp_dir,"Auth.csv")
        def mock_post_init(self):
            return None
        def return_none():
                return None
        def mock_shopping_list_retreive_history(self):
            return pd.DataFrame(data=data_raw_shopping_list)
        def mock_place_my_order_at_supermarket(self,ingredients_to_order):
            return ingredients_to_order
        
        monkeypatch.setattr(CarrefourInteract,'__post_init__',mock_post_init)
        monkeypatch.setattr(CookidooInteract,'__post_init__',mock_post_init)
        monkeypatch.setattr(CookidooInteract,'retrieve_shopping_list',mock_shopping_list_retreive_history)
        monkeypatch.setattr(Client,'place_my_order_at_supermarket',mock_place_my_order_at_supermarket)
        monkeypatch.setattr(utils,'generate_chrome_driver',return_none)
        monkeypatch.setattr(FileManager.authenticate,'__defaults__',(authentication_filename,))
        authentication_client = AuthenticationClient(email="emeric.colombet@gmail.com",password="PASSWORD",content_manager_static=FileManager,shopping_path=temp_dir)
        client = authentication_client.generate_domain_client()
        ingredients_to_order_df = client.go_shopping()
        assert ingredients_to_order_df["Corresponding Carrefour Title"].values.tolist() == ingredients_to_order

