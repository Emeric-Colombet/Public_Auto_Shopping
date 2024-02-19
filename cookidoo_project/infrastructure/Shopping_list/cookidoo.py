from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import pandas as pd 
from typing import List, Optional, Any,TYPE_CHECKING
from time import sleep, time
import logging
import re

#TODO : Utiliser les DTO pour communiquer la donnée, ensuite nous pourrons faire de la data validation sur les email, mdp etc. De plus nous pourrons réutiliser ces DTO d'une adresse mail à l'autre. 
logging.getLogger().setLevel(logging.INFO)
@dataclass
class ShoppingListInteract():
    email : str
    password : str
    """
    This is the Shoppinglist Interface Interaction Object
    
    Attributes
    ----------

    email : str 
        The cookidoo's email to log in
    password : str
        The cookidoo's password to log in
    """

    @abstractmethod
    def retrieve_shopping_list(self) -> pd.DataFrame:
        pass

@dataclass
class CookidooInteract(ShoppingListInteract):
    driver : uc.Chrome
    home_url : str = 'https://cookidoo.fr'
    """
    This is the Cookidoo Interaction Object
    
    Attributes
    ----------
    driver : uc.Chrome 
        The Chrome driver we will use to connect
    home_url : str
        Cookidoo's url to connect"""
    
    def __post_init__(self):
        logging.info("Initializing Cookidoo Interact.")
        self._am_i_connected()

    def retrieve_shopping_list(self) -> pd.DataFrame :
        self.driver.get(self.home_url)
        #self._am_i_connected()
        logging.info("Looking for shopping list page")
        disorganized_shopping_list = self._copy_ingredient_list()
        raw_shopping_list = self._from_disorganized_shopping_list_to_raw_shopping_list(disorganized_shopping_list=disorganized_shopping_list)
        return raw_shopping_list
    
    def _from_disorganized_shopping_list_to_raw_shopping_list(self,disorganized_shopping_list : str) -> pd.DataFrame:
        raw_shopping_list_data = {
            "raw_data_shopping_list" : []
        }
        raw_shopping_list = pd.DataFrame(data=raw_shopping_list_data)
        for line in disorganized_shopping_list.split('\n'):
            if line : 
                if self._contains_square_brackets(line=line):
                    pass
                else : 
                    new_row_for_raw_ingredient = pd.DataFrame(data={"raw_data_shopping_list" : [line]},index=raw_shopping_list.columns)
                    raw_shopping_list = pd.concat([raw_shopping_list,new_row_for_raw_ingredient],ignore_index=True)
        return raw_shopping_list

    def _copy_ingredient_list(self) -> str :
        # Get shopping list :
        self.driver.get("https://cookidoo.fr/shopping/fr-FR")
        # Click on "option" button : 
        logging.info("Looking for option button")
        self.driver.find_element(By.XPATH,'//button[@class="pm--show-web button--secondary"]').click()
        # Click on "Partager" button
        logging.info("Looking for Partager button")
        self.driver.find_element(By.XPATH,'//li[@id="shopping-list-share"]').click()
        # Click on "Copier" button
        logging.info("Looking for Copier button")
        self.driver.find_element(By.XPATH,'//button[@class="copy-to-clipboard"]').click()
        clipboard_text = self.driver.execute_script('return navigator.clipboard.readText()')
        return clipboard_text
        

    
    def _am_i_connected(self):
        self.driver.get(self.home_url)
        # If we can read the username at the profile button, it means that the user is correctly connected. Else we need to connect manually. 
        
        username_connected = self.driver.find_element(By.XPATH,'//h1[@class="core-hero-search__text"]').text
        if not username_connected: 
            logging.warning("User not connected, please log in manualy and we will save cookies.")
            self._connect_manually()
            
        else :
            logging.info("User already connected. We can go shopping.")
            
    def _connect_manually(self):
        """Due to captcha security, we can't automatically connect with email and password in https://cookidoo.fr
            This function will open another tab and you will be able to log in manually and the programm will save cookie for other runs."""
        self.driver.execute_script(f"window.open('{self.home_url}');")
        self.driver.switch_to.window(self.driver.window_handles[1])
        alert_message = "👋👋 Hello friend ! 👋👋 \\n\\nIt seems that you\\'re not logged, \\nPlease connect manually and after flip to the command line to continue the program \\n\\n🙏Do not close tab after connection"
        self.driver.execute_script(f"alert('{alert_message}');")
        self._wait_for_user_text_entry()
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.driver.refresh()
        
    def _wait_for_user_text_entry(self):
        user_command = input("Once you are logged in, please write Yes in the command line for the program to continue.\n")
        if user_command =="Yes":
            logging.info("User said that he is connected, we will reload cookies.")
        else :
            logging.warning("Didn't understand user command, we repeat action.")
            self._wait_for_user_text_entry()
    
    @staticmethod
    def _contains_square_brackets(line):
        """Match the line to know if it contains square brackets"""
        regexp = "\[.*\]"
        square_bracket_match = re.search(regexp,line)
        if square_bracket_match:
            return True
        else :
            return False