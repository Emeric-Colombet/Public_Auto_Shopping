import pytest
from cookidoo_project.domain.ingredient_matcher import IngredientMatcher
from cookidoo_project.infrastructure.content_manager import FileManager
import pandas as pd

ingredients_to_order_dict = {
    "Raw" : ["450 g de carottes","100 g de courgette","30 g de café moulu","300 g de pain","100 g de gruyere","100 g de parmesan"],
    "Unit" : [450,100,30,300,100,100],
    "Ingredient" : ["Carottes","Courgette","café","pain","gruyere","parmesan"]
}
expected_list_of_processed_ingredients = ["carottes","courgette","cafe","emmental","parmigiano"]
expected_list_of_matching_ingredients = [
    "carottes agroecologie filiere qualite carrefour",
    "courgettes premier prix",
    "cafe capsules compatibles nespresso forza intensite 9 l'or espresso",
    "fromage rape emmental fondant carrefour classic'",
    "parmigiano reggiano rape aop carrefour extra"
]

class TestIngredientMatcher():
    """All test around IngredientMatcher object"""

    
    def test_pre_processing_and_manual_processing(self):
        """Here we test all methods used in manual processing function and in pre_processing function"""
        FM = FileManager(
            customer_first_name="Emeric",
            customer_last_name="COLOMBET",
            shopping_list_app="Cookidoo",
            supermarket="Carrefour")
        IM = IngredientMatcher(
            content_manager=FM,
        )
        cleaned_ingredient_to_order_df = IM.manual_processing(structured_ingredients_to_order=pd.DataFrame(data=ingredients_to_order_dict))
        assert cleaned_ingredient_to_order_df["Ingredient"].values.tolist() == expected_list_of_processed_ingredients

    @pytest.mark.usefixtures("generate_drive_history_order_with_empty_structure")
    def test_take_inventory_function(self,generate_drive_history_order_with_empty_structure):
        """Here we test the take_inventory function to check if the reload_order_history and load_global_order_history functions work fine """
        tempdir = generate_drive_history_order_with_empty_structure
        FM = FileManager(
            customer_first_name="Emeric",
            customer_last_name="COLOMBET",
            shopping_list_app="Cookidoo",
            supermarket="Carrefour",
            shopping_path= tempdir)
        IM = IngredientMatcher(
            content_manager=FM
        )
        IM.take_inventory()

    @pytest.mark.usefixtures("generate_drive_history_order_with_empty_structure")
    def test_make_function(self,generate_drive_history_order_with_empty_structure):
        """Here we test the whole match function, with preprocessing step, drive history recovery, and find_historical_correspondance function"""
        tempdir = generate_drive_history_order_with_empty_structure
        FM = FileManager(
            customer_first_name="Emeric",
            customer_last_name="COLOMBET",
            shopping_list_app="Cookidoo",
            supermarket="Carrefour",
            shopping_path= tempdir)
        IM = IngredientMatcher(
            content_manager=FM,
        )
        carrefour_order = IM.match(structured_ingredients_to_order=pd.DataFrame(data=ingredients_to_order_dict))
        assert carrefour_order["Corresponding Carrefour Title"].values.tolist() == expected_list_of_matching_ingredients
        
