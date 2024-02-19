import pytest 
import tempfile
import os
import pandas as pd
import shutil


@pytest.fixture()
def generate_multiple_client_directories():
    with tempfile.TemporaryDirectory() as temp_dir :
        clients_dirname = ["Emeric_COLOMBET","Jean_MICHEL","Philippe_Durand"]
        for client in clients_dirname:
            client_dir = f"{temp_dir}/{client}"
            os.mkdir(client_dir)
        yield temp_dir,clients_dirname
    
#Columns = email, password, first_name, last_name, id, shopping_list_app, shopping_list_email, shopping_list_password, supermarket, supermarket_email, supermarket_password
authentication_data = {
    "email" : ["emeric.colombet@gmail.com","jean.durand@gmail.fr"],
    "password" : ["PASSWORD","MONMOTDEPASSE"],
    "first_name" : ["Emeric","Jean"],
    "last_name" : ["COLOMBET","DURAND"],
    "id" : ["1","2"],
    "shopping_list_app" : ["Cookidoo","Monsieur_Cuisine"],
    "shopping_list_email" : ["emeric.colombet@gmail.com","jean.durand@gmail.fr"],
    "shopping_list_password" : ["PASSWORD","MONMOTDEPASSE"],
    "supermarket" : ["Carrefour","Auchan"],
    "supermarket_email" : ["emeric.colombet@gmail.com","jean.durand@gmail.fr"],
    "supermarket_password" : ["PASSWORD","MONMOTDEPASSE"]
}

@pytest.fixture()
def generate_multiple_client_authentified():
    client_authentication_df = pd.DataFrame(data=authentication_data)
    with tempfile.TemporaryDirectory() as temp_dir :
        authentication_filename = f"{temp_dir}/Auth.csv"
        client_authentication_df.to_csv(authentication_filename)
        yield temp_dir, authentication_filename


@pytest.fixture()
def generate_client_empty_structure():
    with tempfile.TemporaryDirectory() as temp_dir :
        customer_folder_to_create = {
            "customer_shopping_list_folder" : "Emeric_COLOMBET/Shopping_list_provider/Cookidoo",
            "customer_drive_history" : "Emeric_COLOMBET/Carrefour/History/Drive_history",
            "customer_receipt_history" : "Emeric_COLOMBET/Carrefour/History/Receipt_history",
            "customer_global_history" : "Emeric_COLOMBET/Carrefour/History/Global_history",
            "customer_intermediate_data" : "Emeric_COLOMBET/Intermediate_data/"
            }
        for folder_name in customer_folder_to_create:
            root_folder_name = os.path.join(temp_dir,customer_folder_to_create[folder_name])
            os.makedirs(root_folder_name)
        yield temp_dir
@pytest.fixture()
def generate_authentified_client_with_empty_structure():
    client_authentication_df = pd.DataFrame(data=authentication_data)
    with tempfile.TemporaryDirectory() as temp_dir : 
        authentication_filename = f"{temp_dir}/Auth.csv"
        client_authentication_df.to_csv(authentication_filename)
        customer_folder_to_create = {
            "customer_shopping_list_folder" : "Emeric_COLOMBET/Shopping_list_provider/Cookidoo",
            "customer_drive_history" : "Emeric_COLOMBET/Supermarket_provider/Carrefour/History/Drive_history",
            "customer_receipt_history" : "Emeric_COLOMBET/Supermarket_provider/Carrefour/History/Receipt_history",
            "customer_global_history" : "Emeric_COLOMBET/Supermarket_provider/Carrefour/History/Global_history",
            "customer_intermediate_data" : "Emeric_COLOMBET/Intermediate_data/"
            }
        for folder_name in customer_folder_to_create:
            root_folder_name = os.path.join(temp_dir,customer_folder_to_create[folder_name])
            os.makedirs(root_folder_name)
        yield temp_dir

@pytest.fixture()
def generate_drive_history_order_with_empty_structure():
    client_authentication_df = pd.DataFrame(data=authentication_data)
    with tempfile.TemporaryDirectory() as temp_dir : 
        authentication_filename = f"{temp_dir}/Auth.csv"
        client_authentication_df.to_csv(authentication_filename)
        customer_folder_to_create = {
            "customer_shopping_list_folder" : "Emeric_COLOMBET/Shopping_list_provider/Cookidoo",
            "customer_drive_history" : "Emeric_COLOMBET/Supermarket_provider/Carrefour/History/Drive_history",
            "customer_receipt_history" : "Emeric_COLOMBET/Supermarket_provider/Carrefour/History/Receipt_history",
            "customer_global_history" : "Emeric_COLOMBET/Supermarket_provider/Carrefour/History/Global_history",
            "customer_intermediate_data" : "Emeric_COLOMBET/Intermediate_data/"
            }
        # Creating empty structure
        for folder_name in customer_folder_to_create:
            root_folder_name = os.path.join(temp_dir,customer_folder_to_create[folder_name])
            os.makedirs(root_folder_name)
        
        # Adding drive_history folders from data/Pytest_data/Order_history
        history_drive_directories_path = "data/Pytest_data/Drive_history"
        full_history_drive_directories_path = os.path.join(os.getcwd(),history_drive_directories_path)
        for order_directory in os.listdir(full_history_drive_directories_path):
            order_directory_path = os.path.join(full_history_drive_directories_path,order_directory)
            for dir_or_file in os.listdir(order_directory_path):
                full_dir_or_file = os.path.join(order_directory_path,dir_or_file)
                if os.path.isfile(full_dir_or_file):
                    full_file_name = os.path.join(order_directory_path,dir_or_file)
                    order_directory_to_create  = os.path.join(temp_dir,"Emeric_COLOMBET/Supermarket_provider/Carrefour/History/Drive_history",order_directory)
                    if not os.path.exists(order_directory_to_create):
                        os.mkdir(order_directory_to_create)
                    destination_file_name = os.path.join(order_directory_to_create,dir_or_file)
                    shutil.copy(full_file_name,destination_file_name)
        yield temp_dir


