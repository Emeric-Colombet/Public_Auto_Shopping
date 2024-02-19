import pytest 
import os
from time import sleep
import pandas as pd
from spacy.language import Language
from cookidoo_project.infrastructure.content_manager import FileManager
from cookidoo_project.domain.user_defined_exceptions import CustomerCreationException,CustomerAuthenticationException
from cookidoo_project.domain.model import ModelWrapper

data_raw_shopping_list = {
    "raw_data_shopping_list" : [
        "125 g de riz long",
        "3 c. à café d'épices gyros",
        "1 c. à café d'origan déshydraté"
        ]
    }

class TestFileManager():
    """All tests corresponding to file management class.
    We are working on temp directories in order to make tests. 
    You can find those fixtures at conftest.py 
    """

    @pytest.mark.usefixtures("generate_multiple_client_directories")
    def test_list_all_clients(self,generate_multiple_client_directories):
        """Here, we have Three Users (cf conftest.py)"""
        temp_dir, clients_dirname = generate_multiple_client_directories
        file_manager = FileManager(
            customer_first_name="Emeric",
            customer_last_name= "COLOMBET",
            shopping_list_app="Cookidoo",
            supermarket="Carrefour",
            shopping_path = temp_dir
        )
        all_clients_from_file_manager = file_manager.list_all_clients()
        for client in all_clients_from_file_manager:
            assert(client in clients_dirname)


    @pytest.mark.usefixtures("generate_multiple_client_directories")
    def test_raise_error_create_existing_client(self,generate_multiple_client_directories):
        """Here, we will create a folder that already exist and try to raise an error"""
        temp_dir, clients_dirname = generate_multiple_client_directories
        file_manager = FileManager(
            customer_first_name="Emeric",
            customer_last_name= "COLOMBET",
            shopping_list_app="Cookidoo",
            supermarket="Carrefour",
            shopping_path = temp_dir
        )
        with pytest.raises(CustomerCreationException):
            file_manager.create_client()
        
        
    @pytest.mark.usefixtures("generate_multiple_client_directories")
    def test_create_client_structure(self,generate_multiple_client_directories):
        """Here we create a non existing client, and then 
        we verify that all subfolders are correctly created."""
        temp_dir, clients_dirname = generate_multiple_client_directories
        file_manager = FileManager(
            customer_first_name="Juan",
            customer_last_name= "MIGUEL",
            shopping_list_app="Cookidoo",
            supermarket="Carrefour",
            shopping_path = temp_dir
        )
        file_manager.create_client()
        assert file_manager.client_folder_maker.shopping_list_path == f"{temp_dir}/Juan_MIGUEL/Shopping_list_provider/Cookidoo"
        assert file_manager.client_folder_maker.drive_history_path == f"{temp_dir}/Juan_MIGUEL/Supermarket_provider/Carrefour/History/Drive_history"
        assert file_manager.client_folder_maker.receipt_history_path == f"{temp_dir}/Juan_MIGUEL/Supermarket_provider/Carrefour/History/Receipt_history"
        assert file_manager.client_folder_maker.global_history_path == f"{temp_dir}/Juan_MIGUEL/Supermarket_provider/Carrefour/History/Global_history"
        assert file_manager.client_folder_maker.intermediate_data_path == f"{temp_dir}/Juan_MIGUEL/Intermediate_data"

    @pytest.mark.usefixtures("generate_multiple_client_authentified")
    def test_authenticate_customer_ok(self,generate_multiple_client_authentified):
        temp_dir, authentication_filename = generate_multiple_client_authentified
        # TODO : Changer la fonction authenticate pour une classmethod, et pour palier au prbl de authentication_file, faire un mock up pour la variable shopping_path, (sinon on est obligé d'instancier l'objet alors qu'on a pas encore toutes les infos.)
        FileManager.authenticate(email="emeric.colombet@gmail.com",password="PASSWORD",authentication_path=authentication_filename)
    
    @pytest.mark.usefixtures("generate_multiple_client_authentified")
    def test_authenticate_customer_email_nok(self,generate_multiple_client_authentified):
        temp_dir, authentication_filename = generate_multiple_client_authentified
        with pytest.raises(CustomerAuthenticationException):
            FileManager.authenticate(email="emeric.OFZBBEBFOBEZZEBOEF",password="PASSWORD",authentication_path=authentication_filename)
    
    @pytest.mark.usefixtures("generate_multiple_client_authentified")
    def test_authenticate_customer_password_nok(self,generate_multiple_client_authentified):
        temp_dir, authentication_filename = generate_multiple_client_authentified
        with pytest.raises(CustomerAuthenticationException):
            FileManager.authenticate(email="emeric.colombet@gmail.com",password="NOK",authentication_path=authentication_filename)
    
    @pytest.mark.usefixtures("generate_client_empty_structure")
    def test_store_and_load_customer_raw_shopping_list(self,generate_client_empty_structure):
        """In this test we will try to store raw_shopping_list with FileManager method"""
        temp_dir = generate_client_empty_structure
        FM = FileManager(
            customer_first_name="Emeric",
            customer_last_name="COLOMBET",
            shopping_list_app="Cookidoo",
            supermarket="Carrefour",
            shopping_path=temp_dir)
        raw_shopping_list_df = pd.DataFrame(data=data_raw_shopping_list)
        shopping_list_name = "01_01_2023"
        FM.store_raw_shopping_list(raw_shopping_list=raw_shopping_list_df,shopping_list_name=shopping_list_name)
        loaded_shopping_list_df = FM.load_raw_shopping_list(shopping_list_name=shopping_list_name)
        # Assertion
        pd.testing.assert_frame_equal(raw_shopping_list_df,loaded_shopping_list_df)

    @pytest.mark.usefixtures("generate_drive_history_order_with_empty_structure")
    def test_create_global_history_order_file_from_drive_history(self,generate_drive_history_order_with_empty_structure):
        """In this test, we will load all html and csv files generated by history loader. 
            And we will try to create a global history order file from drive History. """
        temp_dir = generate_drive_history_order_with_empty_structure
        FM = FileManager(
            customer_first_name="Emeric",
            customer_last_name="COLOMBET",
            shopping_list_app="Cookidoo",
            supermarket="Carrefour",
            shopping_path=temp_dir)
        # We reload order history
        FM.reload_order_history(history_type="Drive_history")
        assert FM.load_global_order_history().empty == False


class TestModel():
    """All those tests are about loading model with FileManger and testing it.
    """

    def test_load_model(self):
        CM = FileManager(
            customer_first_name="Emeric",
            customer_last_name="COLOMBET",
            shopping_list_app="Cookidoo",
            supermarket="Carrefour")
        spacy_model = CM.load_model()
        assert isinstance(spacy_model,Language)
        #ssMW = ModelWrapper(content_manager=CM)
        
        
