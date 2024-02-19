from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import logging
import pandas as pd
from cookidoo_project.infrastructure.Supermarket.carrefour import CarrefourInteract, SupermarketInteract
from cookidoo_project.infrastructure.Shopping_list.cookidoo import CookidooInteract, ShoppingListInteract
from cookidoo_project.infrastructure.content_manager import ContentManager, FileManager
from cookidoo_project.application import utils 
from cookidoo_project.domain.model import ModelWrapper
from cookidoo_project.domain.ingredient_matcher import IngredientMatcher
if TYPE_CHECKING:
    # This is necessary to prevent circular imports
    from cookidoo_project.infrastructure.content_manager import ContentManager

@dataclass
class Client():
    email : str
    password : str 
    content_manager : ContentManager
    supermarket : SupermarketInteract
    shopping_list : ShoppingListInteract
    model_wrapper : ModelWrapper = field(init=False)
    ingredient_matcher : IngredientMatcher = field(init=False)
    is_new_client : bool = True
    
    def __post_init__(self):
        self.model_wrapper = ModelWrapper(content_manager=self.content_manager)
        self.ingredient_matcher = IngredientMatcher(content_manager=self.content_manager)
    
    def go_shopping(self) -> pd.DataFrame:
        raw_shopping_list = self.retrieve_shopping_list()
        structured_shopping_list = self.structure_shopping_list_from_ner(raw_shopping_list=raw_shopping_list)
        supermarket_matched_shopping_list = self.match_structured_shopping_list_with_order_history(structured_shopping_list=structured_shopping_list)
        order_summary = self.place_my_order_at_supermarket(ingredients_to_order=supermarket_matched_shopping_list)
        return order_summary

    def retrieve_shopping_list(self):
        raw_shopping_list = self.shopping_list.retrieve_shopping_list()
        self.content_manager.store_raw_shopping_list(raw_shopping_list=raw_shopping_list,shopping_list_name=utils.get_date_with_underscore())
        return raw_shopping_list
    
    def structure_shopping_list_from_ner(self, raw_shopping_list : pd.DataFrame) -> pd.DataFrame:
        """This function use a Ner Model who will load the best trained NER model and make prediction with it"""
        structured_shopping_list = self.model_wrapper.predict_shopping_list(raw_shopping_list=raw_shopping_list)
        return structured_shopping_list

    def match_structured_shopping_list_with_order_history(self, structured_shopping_list : pd.DataFrame) -> pd.DataFrame:
        """This function take the structured shopping list as input and return the corresponding 
            supermarket ingredients coming from order history."""
        supermarket_matched_shopping_list = self.ingredient_matcher.match(structured_ingredients_to_order=structured_shopping_list)
        return supermarket_matched_shopping_list
    
    def place_my_order_at_supermarket(self,ingredients_to_order : pd.DataFrame) -> pd.DataFrame:
        """This function will interact with the SupermarketInteract inheritance object in order to place an order.
        
        Params
        ------
        ingredients_to_order : pd.DataFrame
            The list of ingredients to order, with their name/id to find it on the drive supermarket's.
        
        Returns
        -------
            order_summary : pd.DataFrame
            Order summary, with name of founded ingredient, qtt, image? Those information will be used by UI.

        """
        order_summary = self.supermarket.order_ingredient_list(ingredient_list=ingredients_to_order["Corresponding Carrefour Title"].values.tolist())
        return order_summary

    def store_history(self):
        # TODO: Ici on recevra un DTO Carrefour_drive_history. Voir comment on fait pour le stocker: 
        # Est ce que la fct save_to_file est codée dans le DTO. (Il doit donc maîtriser tous les formats de stockage)
        # Ou est ce que la fonction save_to_file est du coté du ContentManager (Il faut donc trouver une norme : pour chaque attribut du DTO, on en fait une colonne, et pour chaque valeur de l'attribut, on en fait une ligne.)
        shopping_cart_dto_list = self.supermarket.export_order_history()
        ContentManager.store_raw_cart_drive()

    def authenticate(self):
        self.content_manager.authenticate(email = self.email,password = self.password)
        

#Peut être mettre ça dans application/authentication. (C'est ici qu'on choisira la méthode de travail (entre le stockage fichier, bdd, le scraping, API...))
#Et renommer ça en FileAuthenticationClient
@dataclass
class AuthenticationClient():
    email : str 
    password : str
    content_manager_static : FileManager
    shopping_path : str = "data/Shopping"
    customer_credentials : pd.Series = field(init=False)

    def __post_init__(self):
        self.customer_credentials = self.content_manager_static.authenticate(self.email,self.password)

    
    def generate_domain_client(self) -> 'Client':
        unique_driver = utils.generate_chrome_driver()
        customer_first_name = self.customer_credentials['first_name']
        customer_last_name = self.customer_credentials['last_name']
        shopping_list_app = self.customer_credentials['shopping_list_app']
        supermarket = self.customer_credentials['supermarket']
        shopping_list_email = self.customer_credentials['shopping_list_email']
        shopping_list_password = self.customer_credentials['shopping_list_password']
        supermarket_email = self.customer_credentials['supermarket_email']
        supermarket_password = self.customer_credentials['supermarket_password']
        CI = CarrefourInteract(email=supermarket_email, password=supermarket_password,driver=unique_driver)
        CkI = CookidooInteract(email = shopping_list_email, password= shopping_list_password,driver=unique_driver)
        FM = FileManager(customer_first_name,customer_last_name,shopping_list_app,supermarket,shopping_path=self.shopping_path)
        client = Client(
            email=self.email,
            password=self.password,
            content_manager=FM,
            supermarket=CI,
            shopping_list=CkI)
        return client
