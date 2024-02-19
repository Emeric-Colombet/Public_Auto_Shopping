from dataclasses import dataclass, field
from cookidoo_project.infrastructure.content_manager import ContentManager
import pandas as pd
from unidecode import unidecode
import spacy
from spacy.lang.fr.examples import sentences 
import re
import logging



@dataclass
class IngredientMatcher():
    content_manager : ContentManager
    ingredient_frequency_cleaned : pd.DataFrame = field(init=False)

    def match(self,structured_ingredients_to_order : pd.DataFrame) -> pd.DataFrame :
        """Run all steps to transform ingredient_to_order Ingredients into real supermarket name/id"""
        all_history_command = self.take_inventory()
        all_history_command_cleaned = self.clean_history_command(all_history_command=all_history_command)
        ingredients_to_order_processed = self.manual_processing(structured_ingredients_to_order=structured_ingredients_to_order)
        self.ingredient_frequency_cleaned = all_history_command_cleaned.groupby(["Title"],as_index=False).count()
        ingredients_to_order_processed["Corresponding Carrefour Title"] = ingredients_to_order_processed["Ingredient"].apply(self.find_historical_correspondance)
        return ingredients_to_order_processed
        
    def take_inventory(self) -> pd.DataFrame :
        """
        In this function, we will loop on Drive history, Receipt history (or both), in order to get the whole 
        order history.  We will save the global order history file to save time. 

        Returns
        -------
        all_history_command : pd.DataFrame 
            The whole commands for the content_manager Supermarker provider.
        """
        self.content_manager.reload_order_history()
        all_history_command = self.content_manager.load_global_order_history()
        return all_history_command
    
    def clean_history_command(self,all_history_command : pd.DataFrame):
        all_history_command_cleaned = all_history_command.copy()
        all_history_command_cleaned = self._remove_accent(column = "Title", command_dataframe=all_history_command_cleaned)
        all_history_command_cleaned = self._remove_capitals(column="Title", command_dataframe=all_history_command_cleaned)
        return all_history_command_cleaned

    def manual_processing(self, structured_ingredients_to_order : pd.DataFrame) -> pd.DataFrame :
        """All manual transformations due to domain processing:
            - Remove list of useless ingredients. (Ex : pain, eau, sel, poivre etc)
            - Manual transformation to make Shopping_list ingredient name match with all_history_command
            """
        ingredients_to_order = self.pre_process_ingredients_to_order(ingredients_to_order = structured_ingredients_to_order)
        ingredients_to_order = self._remove_useless_ingredient(ingredients_to_order=ingredients_to_order)
        ingredients_to_order = self._expert_knowledge(ingredients_to_order=ingredients_to_order)
        return ingredients_to_order
    
    def pre_process_ingredients_to_order(self, ingredients_to_order : pd.DataFrame) -> pd.DataFrame :
        """All pre process steps for ingredients_to_order dataframe: 
            - Removing lines where Ingredient column is null
            - Force Ingredient column type to string
            - Remove accent for Ingredient column
            - Remove Capitals for Ingredient column
            """
        # Remove lines where column Ingredient is null : 
        ingredients_to_order = ingredients_to_order.dropna(subset=['Ingredient'])
        # Change Ingredient column type in order force type as string. 
        ingredients_to_order = ingredients_to_order.astype({'Ingredient':'string'})
        ingredients_to_order = self._remove_accent(column = "Ingredient", command_dataframe = ingredients_to_order)
        ingredients_to_order = self._remove_capitals(column = "Ingredient", command_dataframe = ingredients_to_order)
        return ingredients_to_order


    def _remove_useless_ingredient(self, ingredients_to_order : pd.DataFrame) -> pd.DataFrame :
        """Remove list of useless ingredients like pain, eau, sel, poivre ... """
        list_of_useless_ingredient = ["pain","persil","sel","poivre"]
        ingredients_to_order = ingredients_to_order[~ingredients_to_order["Ingredient"].isin(list_of_useless_ingredient)]
        return ingredients_to_order
    
    def _expert_knowledge(self, ingredients_to_order : pd.DataFrame) -> pd.DataFrame :
        """Empirical tests have shown that some ingredients name coming from Shopping_list 
            doesn't match with all_history_command ingredients name. Like in Cookidoo, the name is parmesan 
            while in Carrefour drive history, its called parmigiano
            """
        # TODO : Cette transformation est en fait propre à Cookidoo, il faut voir pour bouger cette fonction dans le module Cookidoo
        # TODO : Lorsque je ferais un changement de la fonction find_historical_correspondance, ça résoudra les problème de l'ail, du lait et de la crème fraîche.
        corresponding_ingredients = {
            "lait" : "lait demi-ecreme", 
            "gruyere" : "emmental",
            "parmesan" : "parmigiano",
            "creme" : "creme fraiche",
            "ail" : r"ail lautrec"}
        # Create a regex formater for pandas replace fonction. 
        regex_formater = {}
        for key in corresponding_ingredients:
            # We use ^ and $ character in order to replace words that are exactly matching corresponding ingredient.
            regex_formater[(fr'^{key}$')]=corresponding_ingredients[key]
        ingredients_to_order["Ingredient"] = ingredients_to_order["Ingredient"].replace(regex=regex_formater)
        return ingredients_to_order

    def find_historical_correspondance(self,ingredient : str):
        """Recover the ingredient from customer's order history list.
            - If the ingredient to recover is one word, we will match it in one time. 
            - If the ingredient to recover is composed of multiple words, we will match one ingredient, and match 
                the second on the result of the first match. 
        Parameters
        ----------
        ingredients : string of n words
            ingredient to order
        Returns
        -------
        corresponding_title : string of n words
            The most common ingredient from order history, matching the input ingredient
        """
        number_of_occurence = len(ingredient.split())
        stop_words = ["de"]
        if number_of_occurence < 2 :
            try :
                best_matching_ingredient_name = self.find_name_for_best_matching_ingredient(ingredient=ingredient)
            except ValueError:
                logging.error(f"No match found for ingredient {ingredient}")
                best_matching_ingredient_name = "Not found"
            return best_matching_ingredient_name
        else :
            ingredient_frequency_cleaned_matching = self.ingredient_frequency_cleaned.copy()
            for occurence in ingredient.split():
                logging.info(f"Nous sommes dans le for, à l'occurence {occurence}") 
                # In the case of : Viande de boeuf, we want to look at viande and boeuf words, so we avoid stop words matching
                if occurence not in stop_words: 
                    try :
                        ingredient_frequency_cleaned_matching = ingredient_frequency_cleaned_matching[ingredient_frequency_cleaned_matching["Title"].str.contains(fr'\b{occurence}(e|s|\b)')]
                    except ValueError:
                        logging.error(f"No match found for ingredient {occurence}")
                        corresponding_title = "Not found"
                        return corresponding_title
            if len(ingredient_frequency_cleaned_matching) == 0 :
                logging.info(f"No match found for ingredient {occurence}")
                return "Not found"
            else :
                id_occurence_max = ingredient_frequency_cleaned_matching["Description"].idxmax()
                logging.info(f"Id occurence Max : {id_occurence_max}")
                logging.info(f"Ingredient frequency cleaned matching : {ingredient_frequency_cleaned_matching}")
                corresponding_title = ingredient_frequency_cleaned_matching.loc[id_occurence_max]["Title"]
                return corresponding_title
    
    def find_name_for_best_matching_ingredient(self, ingredient : str):
        """This function will search all the history ingredients that match the ingredient name."""
        # TODO : Changer la façon de rechercher pour privilégier les lignes où l'ingrédient en question apparait au début du nom. 
        # Exemple : Si je cherche du basilic, le match avec la plus grande occurence est : sauce pesto alla genovese basilic frais barilla alors que nous on préfèrerait avoir Basilic FLORETTE
        id_best_matching_ingredient = self.ingredient_frequency_cleaned[self.ingredient_frequency_cleaned["Title"].str.contains(fr'\b{ingredient}(e|s|\b)')]["Description"].idxmax()
        best_matching_ingredient_name = self.ingredient_frequency_cleaned.iloc[id_best_matching_ingredient]["Title"]
        return best_matching_ingredient_name
        

    @staticmethod
    def _remove_accent(column : str, command_dataframe : pd.DataFrame) -> pd.DataFrame:
        """This static method, remove accent of the column `title` for the command_dataframe object."""
        command_dataframe[column] = command_dataframe[column].apply(unidecode)
        return command_dataframe
    
    @staticmethod
    def _remove_capitals(column : str, command_dataframe : pd.DataFrame) -> pd.DataFrame:
        """This static method remove capitals of the column `title` for the command dataframe object."""
        command_dataframe[column] = command_dataframe[column].str.lower()
        return command_dataframe