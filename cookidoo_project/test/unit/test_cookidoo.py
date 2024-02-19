import pytest
from pydantic.error_wrappers import ValidationError
from cookidoo_project.infrastructure.Shopping_list.cookidoo import CookidooInteract
from cookidoo_project.application.utils import generate_chrome_driver


class TestCookidoo():

    def test_instanciate_cookidoo_interact(self,monkeypatch):
        """This function aims to import and instanciate a Cookidoo object"""
        def mock_post_init(self):
            return None
        monkeypatch.setattr(CookidooInteract,'__post_init__',mock_post_init)
        cookidoo_interact = CookidooInteract(email="emeric.colombet@gmail.com",password="Password",driver=None)
    
    