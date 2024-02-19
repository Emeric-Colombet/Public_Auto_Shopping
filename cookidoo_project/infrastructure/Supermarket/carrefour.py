from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from time import sleep 
import undetected_chromedriver as uc
import logging
import pickle 
import os 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pandas as pd 
logging.getLogger().setLevel(logging.INFO)

#TODO : Faire une méta class carrefour interact qui prend en entrée toutes les autres classes carrefour connect, carrefour History  etc
#self.driver.find_element(By.XPATH,'//button[@id="data-account"]')



@dataclass
class SupermarketInteract(ABC):

    @abstractmethod
    def export_order_history(self):
        pass
    @abstractmethod
    def order_ingredient_list(self,ingredient_list : list) -> pd.DataFrame :
        pass



@dataclass
class CarrefourInteract(SupermarketInteract):
    """This is the entry fonction in order to work with Carrefour scraping services.
    Be carefull to kill other running chrome instance."""
    email : str 
    password : str
    driver : uc.Chrome 
    home_url : str = 'https://www.carrefour.fr/'
    
    def __post_init__(self):
        carrefour_connect = CarrefourConnect(self.email,self.password,self.driver)
        self.driver = carrefour_connect.connect()
        
    def RUN(self):
        print("Ready to go !!")
        # TODO : Ne pas faire les lignes carrefour_retrive_history et carrefour_retrieve_history.export_all_commands
        # TODO : Ajouter des options au script pour savoir si on fait une récupération de l'entièreté de l'historique, 
        # TODO : Ajd l'historique des commandes est en dur pour une partie, il faudrait le mettre en configuration, et au fur et à mesure des commandes, ajouter les nouvelles commandes à l'historique. On regarde le numéro des dernières commandes de ces 3 derniers mois, et pour chaque commande qui ne figure pas dans la liste des ancienne commandes, on la rajoute. 
        #carrefour_retrieve_history = CarrefourRetrieveHistory(self.driver)
        #carrefour_retrieve_history.export_all_commands()
        sleep(12000)
        """
        order_list = ["Poitrine crue fumée à l'ancienne","Lardons fumés CARREFOUR EXTRA","Biscuits sablés nappés au chocolat au lait Granola LU","Viande hachée pur bœuf 15% MG CARREFOUR LE MARCHE"]
        #TODO : Ajouter dans le premier ajout au panier une option pour cocher qu'on veut soiit un retrait au drive d'AVON, soit une livraison etc.
        
        """

    def export_order_history(self):
        """This function will implement CarrefourRetrieveHistory class, which lead to recover purchase history. 
            It depends on Supermarket provider, but there is two types of history : 
                - Drive history : Ingredients purchased on internet.
                - Receipt history : Ingredients purschased in a physical shop.
        """
        # TODO : Faire en sorte que l'export History : 
            # 1) Récupère les commandes : (soit de type History, soit de type receipt)
            # 2) Récupère les page html correspondantes et les formattent en un DTO (Avec un CarrefourDriveHistoryFormater), 
        carrefour_retrieve_history = CarrefourRetrieveHistory(self.driver)
        carrefour_retrieve_history.export_all_commands()
        return True
    
    def order_ingredient_list(self, ingredient_list : list) -> pd.DataFrame:
        """This function will use CarrefourOrder class to order ingredients. 
        
        Params
        ------
        ingredient_list : list 
            The list of ingredients complete name optimise for drive order.

        Returns
        -------
        order_summary : pd.DataFrame
            Order summary, with name of founded ingredient, qtt, image? Those information will be used by UI.
        """
        carrefour_order = CarrefourOrder(ingredient_list,self.driver,self.home_url)
        order_summary = carrefour_order.order_all_ingredients()
        logging.info("Order done please see your cart to purchase.")
        return order_summary



@dataclass
class CarrefourConnect:
    email : str
    password : str 
    driver : uc.Chrome
    home_url : str = "https://carrefour.fr"
    connection_method : str = "Cookies_method"

    """
    This is the Carrefour connection  object. 

    params:
        - email : The email to sign in 
        - password : The password to sign in 
        - driver : The driver we will use to make connection*
        - connection url : Url used to connect user
        - home_url : carrefour home url
        - connection method : This is the method use to make the application connect : 
            - 1. Cookies_method : We will try to make use of cookies, or provide the connection interface in order to log in manualy
            - 2. Auto_connect_method : Be carreful, this means that each time you will launch the app, it will perform a connection.  

    
    """
    def connect(self):
        if self.connection_method == "Cookies_method" :
            self._am_i_connected()
            return self.driver
        elif self.connection_method == "Auto_connect_method":
            self._auto_connect()
            return self.driver
        else : 
            raise SyntaxError(f"Please provide a possible connection method !! Cookies_method or Auto_connect_method")
        

    def _am_i_connected(self):
        logging.info("Check connection")
        self.driver.get(self.home_url)
        connection_icon = self.driver.find_element(By.XPATH,'//button[contains(@class,"mainbar-item mainbar-item--variation-primary")]')
        connected_aria_label = connection_icon.get_attribute("aria-label")
        if "Bonjour, vous êtes connecté en tant que" in connected_aria_label :
            logging.info("Use of cookies OK! Connected")
        else : 
            logging.info("Not connected, try to connect manualy please")
            self._connect_manually()

    
    def _connect_manually(self):
        """Due to captcha security, we can't automatically connect with email and password in https://carrefour.fr
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

    def _auto_connect(self):
        logging.info("Auto connecting to carrefour.fr")
        self.driver.get(self.home_url)
        try :
            self.driver.find_element(By.XPATH,'//button[@id="onetrust-reject-all-handler"]').click()
        except :
            logging.warn("We couldn't load cookies, maybe because they are already loaded.")
        self.driver.find_element(By.XPATH,'//button[@id="data-account"]').click()
        #Todo faire en sorte de récupérer la sélection pour refaire un findelement avec /
        self.driver.find_element(By.XPATH,'//a[@class="pl-navigation-item pl-navigation-item--secondary"]').click()
        self.driver.find_element(By.XPATH,'//input[@id="idToken1"]').send_keys(self.email)
        self.driver.find_element(By.XPATH,'//input[@id="idToken2"]').send_keys(self.password)
        self.driver.find_element(By.XPATH,'//input[@id="loginButton_0"]').click()
        logging.info("Auto connection done!")

@dataclass
class CarrefourRetrieveHistory:
    """THIS FUNCTION IS CURRENTLY NOT WORKING"""
    driver : uc.Chrome  
    #TODO : Faire une fonction retrieve all historical data, et une fonction retrieve last_3_month_historical_data
    #Dans la fonction retrieve_all_historical data, on prend en entrée une liste de numéros de commande (faite à la main), 
    #Puis on part du principe que le programme ne cherchera que les n dernières commandes (celles qui sont sur le site mais pas dans la liste des commandes déjà sauvées.)
    # Si on a une commande nouvelle sur le site, et pas dans la liste de l'historique des commandes (locales en html), alors il ajoute tous les nouvelles. 
    def retrieve_history_last_order(self):
        logging.debug("Looking for history")
        #Open new tab 
        self.driver.switch_to.new_window('tab')
        # Switch to the new window and open new URL
        self.driver.switch_to.window(self.driver.window_handles[1])
        new_url = 'https://www.carrefour.fr/mon-compte/mes-achats/en-ligne'
        self.driver.get(new_url)
        last_orders = self.driver.find_elements(By.XPATH,'//div[@class="order-item__summary"]')
        logging.info("Click sur le premier bouton !!!!")
        last_orders[0].click()
        # Waiting for the script to load all the html code and specialy the 'article' tag.
        WebDriverWait(self.driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH,'//article[@class="ds-product-card--order ds-product-card-refonte"]')))
        ingredient_list = self.driver.find_element(By.XPATH,'//section[@class="order-detail"]')
        html_ingredient_list = self.driver.execute_script("return arguments[0].outerHTML;",ingredient_list)
        f = open("data/order_history/latest/last_order.html", "w")
        f.write(html_ingredient_list)
        f.close()
        logging.debug("Logged last order from customer order history.")
        #Les lignes ci dessous permettront d'exporter le tableau d'éléments de tous les ingrédients 
        #self.driver.find_elements()
        #texte = driver.find_element(By.XPATH,'//ul[@id="data-plp_produits"]')
        

        logging.debug("History retrieving finished")
    def export_all_commands(self):
        all_command_in_2022 = [538601485,542689499,547456837,533821339,539349536,542945967,534930175,536289624,547893696,543814699,548242566,540234501,547648462,543153774,550313593,539241835,539066466,533888819,537321426,535769057,526289473,522201346,522353001,526748139,529013885,530140363, 521653038,530848659,525059598,527300322,517522873,517261322,528377989,519092479,522823526,521024011,521867942,526807307]
        for command in all_command_in_2022: 
            self._create_folder_if_not_exist(str(command))
            #Open new tab 
            self.driver.switch_to.new_window('tab')
            # Switch to the new window and open new URL
            self.driver.switch_to.window(self.driver.window_handles[1])
            new_url = f"https://www.carrefour.fr/mon-compte/mes-achats/en-ligne/{str(command)}"
            self.driver.get(new_url)
            # Waiting for the script to load all the html code and specialy the 'article' tag.
            try :
                WebDriverWait(self.driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH,'//article[@class="ds-product-card--order ds-product-card-refonte"]')))
            except TimeoutException: 
                print(f"Failed to load the following command {str(command)}")
                continue
            ingredient_list = self.driver.find_element(By.XPATH,'//section[@class="order-detail"]')
            html_ingredient_list = self.driver.execute_script("return arguments[0].outerHTML;",ingredient_list)
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            f = open(f"data/order_history/{str(command)}/exported_order.html", "w")
            f.write(html_ingredient_list)
            f.close()
            logging.debug("Logged last order from customer order history.")
    
    def _create_folder_if_not_exist(self, order_name : str):
        folder_name = f"data/order_history/{order_name}"
        if os.path.exists(folder_name):
            pass
        else : 
            os.makedirs(folder_name)
            logging.debug(f"Created folder {folder_name}")



@dataclass
class CarrefourOrder:
    order_list : list
    driver : uc.Chrome 
    home_url : str 

    def order_all_ingredients(self) -> pd.DataFrame :
        """
        Loop on ingredient list and try to add each one to the cart.
        
        Returns
        -------
        order_summary : pd.DataFrame
            Order summary, with name of founded ingredient, qtt, image? Those information will be used by UI.
        """
        # TODO : Use implement order summary to keep track of ingredients founded, quantity and initial ingredient expected. In order to recap those information in front end.
        order_summary = pd.DataFrame()
        self.driver.get(self.home_url)
        for ingredient in self.order_list:
            if ingredient != "Not found":
                self.order_one_ingredient(ingredient=ingredient)
        return order_summary

    
    def order_one_ingredient(self,ingredient) -> pd.DataFrame : 
        """
        This function will look for the ingredient into search bar, and click on the add button of the first resulting ingredient. 
            If the same ingredient was previously added, it will click to the `+` button to order this ingredient a second time.
        Returns
        -------
        order_summary : pd.DataFrame
            TO IMPLEMENT !! Order summary, with name of founded ingredient, qtt, image? Those information will be used by UI. 
        """
        # TODO : TEster cet example là : Courge butternut en cubes CARREFOUR
        # Il faut avoir la capacité de reconnaître le message "Nous avons beau chercher, nous ne retrouvons pas..."
        # En face de ce message là, il faut peut être changer de méthode, ajouter ça à la liste des produits non trouvés. 
        search_bar = self.driver.find_element(By.XPATH,'//input[@name="q"]')
        logging.info(f"Looking for ingredient {ingredient}")
        #On fait un ctrl A, mais selenium ne fonctionne qu'en qwerty, donc il faut lui dire qu'on fait un ctrl q
            #WARNING : Sous docker le ctrl q ne marche pas comme prévu, mais le ctrl a marche. Donc entre le local et le docker ce n'est pas le même code.
            # Il est temps d'utiliser une variable pour les différencier.  
        #search_bar.send_keys(Keys.CONTROL, 'q')
        search_bar.send_keys(Keys.CONTROL, 'a')
        #On supprime le texte précédent
        search_bar.send_keys(Keys.BACKSPACE)
        search_bar.send_keys(ingredient)
        search_button = self.driver.find_element(By.XPATH,'//button[@class="pl-button header-search__submit-btn pl-button--tone-main pl-button--variation-primary"]')
        search_button.click()
        print("Before fisrt ingredient")
        first_ingredient_of_result_list = self.driver.find_elements(By.XPATH,'//div[@class="product-list advertised-product-list product-list"]//li[@class="product-grid-item"]')[0]
        print("After first ingredient")
        # Important !! Si vous voulez chercher un sous élément d'un objet find_element, il faut ajouter un . au XPath habituel, ce qui signifie de rechercher à partir de cet élément là et parmis tous les sous éléments possibles. 
        print("Before cart button")
        cart_button = first_ingredient_of_result_list.find_elements(By.XPATH,'.//button[@class="ds-button add-to-cart-cta ds-button--icon ds-button--primary add-to-cart__plus"]')
        print("After cart button")
        if len(cart_button) == 0 :
            logging.info(f"No cart button disponible, try with + button...")
            print("Before plus button")
            plus_button = first_ingredient_of_result_list.find_elements(By.XPATH,'.//button[@class="quantity-counter__action"]')
            print("After plus button")
            if len(plus_button) == 0 :
                logging.info("It seems that there isn't any product correponding to your research")
            else : 
                logging.info("Increase ingredient quantity")
                print("Before plus button click")
                plus_button[1].click()
                print("After plus button click")
        else :
            logging.info("Adding to cart")
            cart_button[0].click()
            logging.info("Cart added")
        return pd.DataFrame()




    