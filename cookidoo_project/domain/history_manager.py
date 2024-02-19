import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import csv 
from dataclasses import dataclass
import os, sys
from time import sleep
import logging


@dataclass
class HistoryManager:
    """
        THIS CLASS IS NOT FUNCTIONAL AND WILL BE CHANGED IN FUTUR
        This class retreive html history of past orders. 
        Loop on each order and export ingredient name to csv all whole customer history. 
        TODO : Ajouter cette même feature pour des historiques de commandes ayant eu lieu dans un magasin (ticket de caisse)
        TODO : Pour l'historique de commande drive, le nom des aliments peut être amené à changer, et si on effectue la recherche suivante dans la barre de recherche carrefour : 
            carottes agroecologie filiere qualite carrefour 	
            Le site nous retourne des poireaux. Pour éviter ce piège il faut réussir à retrouver le vrai nom (ID) de l'ingrédient : carottes-agroecologie-filiere-qualite-carrefour-3523680426818
            Et à ce moment là, si l'ingrédient n'est pas dans le drive d'Avon (et c'est le cas), le site propose automatiquement des produits de remplacement.
            Pour y arriver, la meilleure solution est de taper dans google le nom de l'ingrédient, de cliquer sur le premier lien carrefour qui répond, et récupérer ce qu'il y a dans l'url après https://www.carrefour.fr/p/

        """
    order_history_path = "data/order_history"
    CHROMEDRIVER_PATH = 'data/chromedrivers/chromedriver'

    def convert_html_history_to_csv(self):
        root_project_absolute_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        folder_list = os.listdir(self.order_history_path)
        header = ["Title","Description","Quantity","Price"]
        for folder in folder_list:
            ingredient_list = []
            relative_html_command_path = f"{self.order_history_path}/{folder}/exported_order.html"
            absolute_html_command_path = os.path.join(root_project_absolute_path,relative_html_command_path)
            driver = uc.Chrome(driver_executable_path=self.CHROMEDRIVER_PATH,headless=True)
            driver.get(f"file://{absolute_html_command_path}")
            all_articles = driver.find_elements(By.XPATH,'//article[@class="ds-product-card--order ds-product-card-refonte"]')
            for article in all_articles :
                order_info = article.find_element(By.XPATH,'.//div[@class="ds-product-card--order__info"]')
                order_amounts = article.find_element(By.XPATH,'.//div[@class="ds-product-card--order__amounts"]')
                try :
                    title, description = order_info.text.split('\n')
                except ValueError: 
                    logging.warning(f"Raised value error, it seems that the values {order_info.text} failed.")
                    continue
                quantity, price = order_amounts.text.split('\n')
                row = [title, description, quantity, price]
                ingredient_list.append(row)
            relative_csv_command_path = f"{self.order_history_path}/{folder}/exported_order.csv"
            with open(relative_csv_command_path, 'w', encoding='UTF8', newline='') as f:
                writer = csv.writer(f)
                # write the header
                writer.writerow(header)
                # write multiple rows
                writer.writerows(ingredient_list)
                logging.info(f"Saved csv orders for {str(folder)} command.")

