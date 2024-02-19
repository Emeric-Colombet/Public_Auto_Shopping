from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import os
import logging
from cookidoo_project.domain.user_defined_exceptions import CustomerCreationException, CustomerAuthenticationException
from cookidoo_project.application.utils import get_date_with_underscore
import pandas as pd 
from spacy.language import Language
import spacy 

class ContentManager(ABC):

    @abstractmethod
    def create_client(self) : 
        pass

    @abstractmethod
    def list_all_clients(self):
        pass

    @staticmethod
    @abstractmethod
    def authenticate(email : str, password : str, authentication_path : str = "data/Auth.csv" ) -> pd.Series :
        pass

    @abstractmethod
    def store_raw_shopping_list(self, raw_shopping_list : pd.DataFrame, shopping_list_name : str) -> pd.DataFrame :
        pass
    
    @abstractmethod
    def load_raw_shopping_list(self,shopping_list_name : str) -> pd.DataFrame :
        pass

    @abstractmethod
    def load_model(self) -> Language:
        pass

    @abstractmethod
    def save_structured_shopping_list(self,structured_shopping_list : pd.DataFrame):
        pass
    
    @abstractmethod
    def load_structured_shopping_list(self,structured_shopping_list_name : str) -> pd.DataFrame:
        pass

    @abstractmethod
    def reload_order_history(self,history_type : str = "Drive_history") -> pd.DataFrame : 
        pass
    
    @abstractmethod
    def load_global_order_history(self) -> pd.DataFrame:
        pass

@dataclass
class ClientFolderTree():
    client_dir_name : str 
    shopping_list_app : str 
    supermarket : str 
    shopping_list_path : str = field(init=False)
    drive_history_path : str = field(init=False)
    receipt_history_path : str= field(init=False)
    global_history_path : str = field(init=False)
    intermediate_data_path : str = field(init=False)

    def __post_init__(self):

        # data/Shopping/Emeric_COLOMBET/Shopping_list_provider/Cookidoo
        self.shopping_list_path = os.path.join(
            self.client_dir_name,
            "Shopping_list_provider",
            self.shopping_list_app)
        
        # data/Shopping/Emeric_COLOMBET/Supermarket_provider/Carrefour/History/Drive_history
        self.drive_history_path = os.path.join(
            self.client_dir_name,
            "Supermarket_provider",
            self.supermarket,
            "History/Drive_history")

        # data/Shopping/Emeric_COLOMBET/Supermarket_provider/Carrefour/History/Receipt_history
        self.receipt_history_path = os.path.join(
            self.client_dir_name,
            "Supermarket_provider",
            self.supermarket,
            "History/Receipt_history")

        # data/Shopping/Emeric_COLOMBET/Supermarket_provider/Carrefour/History/Global_History
        self.global_history_path = os.path.join(
            self.client_dir_name,
            "Supermarket_provider",
            self.supermarket,
            "History/Global_history")
        # data/Shopping/Emeric_COLOMBET/Intermediate_data
        self.intermediate_data_path = os.path.join(
            self.client_dir_name,
            "Intermediate_data")

    def create_all_folders(self):
        self._create_shopping_folder
        self._create_supermarket_folders
        self._create_intermediate_folder

    def _create_shopping_folder(self):
        os.makedirs(self.shopping_list_path)
    
    def _create_supermarket_folders(self):
        os.makedirs(self.drive_history_path)
        os.makedirs(self.receipt_history_path)
        os.makedirs(self.global_history_path)

    def _create_intermediate_folder(self):
        os.makedirs(self.intermediate_data_path)



@dataclass
class FileManager(ContentManager):
    customer_first_name : str
    customer_last_name : str
    # TODO : Faire un DTO pour cet objet, utiliser pydantic pour checker les formats et valeurs de la variable `shopping_list_app`
    shopping_list_app : str
    supermarket : str 
    shopping_path : str = "data/Shopping"
    model_path : str = "data/models"
    client_folder_maker : ClientFolderTree = field(init=False)

    def __post_init__(self):
        self.client_dir_name = f"{self.shopping_path}/{self.customer_first_name}_{self.customer_last_name}"
        self.client_folder_maker = ClientFolderTree(
            client_dir_name=self.client_dir_name,
            shopping_list_app=self.shopping_list_app,
            supermarket=self.supermarket)

    def create_client(self):
        """This function create a folder from client name
        We leave the possibility to create already existing customers. 
        (So the possibility of an error), because we want these cases to be handled by the Client object."""

        try : 
            os.mkdir(self.client_dir_name)
        except FileExistsError:
            raise CustomerCreationException("We couldn't create client because a file with similar name already exis")
        except FileNotFoundError:
            raise CustomerCreationException("We couldn't create client because it names isn't reachable by our file manager.\
                                          Maybe look at `/` characters in your name?")
        self.client_folder_maker.create_all_folders()


    def list_all_clients(self) -> list[str]:
        list_of_all_clients = []
        for client in os.listdir(self.shopping_path):
            list_of_all_clients.append(client)
        return list_of_all_clients
    
    #TODO : Utiliser un DTO pour ne pas avoir à utiliser raw_shopping_list et shopping_list_name
    def store_raw_shopping_list(self, raw_shopping_list : pd.DataFrame, shopping_list_name : str) -> pd.DataFrame :
        """Store input df into csv at path shopping_list_path"""
        raw_shopping_list_csv_path = os.path.join(self.client_folder_maker.shopping_list_path,f"{shopping_list_name}.csv")
        raw_shopping_list.to_csv(raw_shopping_list_csv_path,index=False)
        return raw_shopping_list
    
    def load_raw_shopping_list(self,shopping_list_name : str) -> pd.DataFrame :
        """Load shopping_list (csv), from shopping_list_name"""
        raw_shopping_list_csv_path = os.path.join(self.client_folder_maker.shopping_list_path,f"{shopping_list_name}.csv")
        raw_shopping_list = pd.read_csv(raw_shopping_list_csv_path)
        return raw_shopping_list
    
    def load_model(self):
        last_model = os.path.join(self.model_path,"model-last")
        model  = spacy.load(last_model)
        return model
    
    def save_structured_shopping_list(self,structured_shopping_list : pd.DataFrame):
        order_folder_path = os.path.join(self.client_folder_maker.intermediate_data_path,f"{get_date_with_underscore()}.csv")
        self.create_order_folder_path_if_doesnt_exist(order_folder_path=order_folder_path)
        logging.info(f"Saving structured_shopping_list to {order_folder_path}")
        structured_shopping_list.to_csv(order_folder_path,index=False)
    
    def load_structured_shopping_list(self,structured_shopping_list_name : str) -> pd.DataFrame:
        order_folder_path = os.path.join(self.client_folder_maker.intermediate_data_path,structured_shopping_list_name)
        structured_shopping_list = pd.read_csv(order_folder_path)
        return structured_shopping_list


    def create_order_folder_path_if_doesnt_exist(self,order_folder_path : str):
        isExist = os.path.exists(order_folder_path)
        if isExist :
            logging.info(f"Folder {order_folder_path} already exist, working with it")
        else : 
            logging.info(f"Folder {order_folder_path} doesn't exist, creating it.")

    def reload_order_history(self,history_type : str = "Drive_history") : 
        """Loop on all order history, look at each order, find history csv file, add it to 
            the main dataframe and save it into global_history_path.
    
        Parameters
        ----------
        history_type : str
            Type of order history we want to loop on. It can be :
                - Drive_history : if you want only drive orders
                - Receipt_history : if you want only receipt orders
                - Both : if you want Drive_history and Receipt_history. 

        Returns 
        -------
        global_orders : pd.DataFrame
            Dataframe containing all the past orders with their names etc.


            """
        global_orders = pd.DataFrame(columns=["Title","Description","Quantity","Price"])

        if history_type == "Drive_history":
            for directory in os.listdir(self.client_folder_maker.drive_history_path):
                order_csv_file_name = os.path.join(self.client_folder_maker.drive_history_path,directory,"exported_order.csv")
                order_dataframe = pd.read_csv(order_csv_file_name)
                global_orders = pd.concat([global_orders,order_dataframe],ignore_index=True)
            global_order_path = os.path.join(self.client_folder_maker.global_history_path,"global_order.csv")
            global_orders.to_csv(global_order_path,index=False)
            logging.info("All Drive History orders are correctly reloaded, global history file will now contain it.")
        
        elif history_type == "Receipt_history":
            raise NotImplementedError
        
        elif history_type == "Both":
            raise NotImplementedError
    
    def load_global_order_history(self) -> pd.DataFrame :
        global_order_path = os.path.join(self.client_folder_maker.global_history_path,"global_order.csv")
        global_dataframe = pd.read_csv(global_order_path)
        return global_dataframe
        

    @staticmethod
    def authenticate(email : str, password : str, authentication_path : str = "data/Auth.csv" ) -> pd.Series :
        """We will load authenticate file (pandas df) and search for matching email and matching pwd
        
        Parameters
        ----------
        authentication_path : str 
            Path used for authentication. (We use this in order to change paths when testing.)
        email : str 
            Customer email, used to authenticate.
        password : str 
            Customer password, used to authenticate.
        
        Raises
        ------
        AuthenticationError
            Unable to authenticate customer.
        
        Returns
        -------
        file_manager : FileManager
            FileManager object instanciated with corresponding customer information
        """

        authentication_df = pd.read_csv(authentication_path)
        email_matching_line_df = FileManager._recover_authentication_email(authentication_df,email)
        customer_credentials = FileManager._authenticate_password_given_email(email_matching_line_df,password)
        return customer_credentials
        #Columns = email, password, first_name, last_name, id, shopping_list_app, shopping_list_email, shopping_list_password, supermarket, supermarket_email, supermarket_password
    
    @staticmethod
    def _recover_authentication_email(authentication_df : pd.DataFrame, email : str) -> pd.DataFrame :
        regex_email_exact_match = fr"^{email}$"
        matching_emails = authentication_df["email"].str.match(regex_email_exact_match)
        number_of_exactly_matching_email = len(matching_emails[matching_emails].index.values.tolist())
        if number_of_exactly_matching_email == 0 :
            raise CustomerAuthenticationException("This email was not found, Have you already created an account?")
        elif number_of_exactly_matching_email > 1 : 
            raise CustomerAuthenticationException("Internal error, it seems that we found too many matching customer")
        else :
            corresponding_index = matching_emails[matching_emails].index.values.tolist()[0]
            return authentication_df.iloc[corresponding_index]
        
    @staticmethod
    def _authenticate_password_given_email(email_matching_line_df : pd.Series, password : str) -> pd.Series :
        correct_password = email_matching_line_df["password"]
        if password != correct_password:
            raise CustomerAuthenticationException("Sorry, but this is not the correct password for this email.")
        else :
            logging.info("Correctly logged !")
            return email_matching_line_df