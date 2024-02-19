import pytest 
import os
from time import sleep
import pandas as pd
from spacy.language import Language
from cookidoo_project.application.utils import get_date_with_underscore
from cookidoo_project.infrastructure.content_manager import FileManager
from cookidoo_project.domain.user_defined_exceptions import CustomerCreationException,CustomerAuthenticationException
from cookidoo_project.domain.model import ModelWrapper
from cookidoo_project.infrastructure.Shopping_list.cookidoo import CookidooInteract
from cookidoo_project.infrastructure.Supermarket.carrefour import CarrefourInteract
from cookidoo_project.domain.client import AuthenticationClient


class TestModel():
    """This class will test model wrapper instance with a functionnal manner. 
        We will test the whole process, from loading to prediction."""
    def test_model_wrapper_predict_one_sentence_correctly(self):
        CM = FileManager(
            customer_first_name="Emeric",
            customer_last_name="COLOMBET",
            shopping_list_app="Cookidoo",
            supermarket="Carrefour")
        MW = ModelWrapper(content_manager=CM)
        ground_truth_dict = {'QUANTITY': '125', 'UNIT': 'g', 'FOOD': 'riz long'}
        response = MW.ner_labelisation_one_sentence("125 g de riz long").ents
        predicted_dict = {}
        for word in response:
            predicted_dict[word.label_] = word.text
        assert ground_truth_dict == predicted_dict
    
    @pytest.mark.usefixtures("generate_client_empty_structure")
    def test_model_wrapper_predict_multiple_sentences_correctly(self,generate_client_empty_structure):
        temp_dir = generate_client_empty_structure
        expected_multiple_prediction_dict = {
            "Raw" : ["125 g de riz long","200 g de petits pois écossés"," 100 g de lait "],
            "Quantity" : ["125","200","100"],
            "Unit" : ["g","g","g"],
            "Ingredient" : ["riz long","petits pois","lait"]
        }
        expected_multiple_prediction_df = pd.DataFrame(data=expected_multiple_prediction_dict)
        input_data_dict = {
            "raw_data_shopping_list" : ["125 g de riz long","200 g de petits pois écossés"," 100 g de lait "]
        }
        input_data_df = pd.DataFrame(data=input_data_dict)
        CM = FileManager(
            customer_first_name="Emeric",
            customer_last_name="COLOMBET",
            shopping_list_app="Cookidoo",
            supermarket="Carrefour",
            shopping_path=temp_dir)
        MW = ModelWrapper(content_manager=CM)
        model_output_df = MW.predict_shopping_list(raw_shopping_list=input_data_df)
        # Assert with pandas that output result for prediction worked well.
        pd.testing.assert_frame_equal(model_output_df,expected_multiple_prediction_df)
        saved_and_loaded_model_output = CM.load_structured_shopping_list(structured_shopping_list_name=f"{get_date_with_underscore()}.csv")
        # Because of saving into CSV, quantitty column is now numpy.int. We want to work with str for simplicity, so we hardcode column dtype in order to pass tests.
        saved_and_loaded_model_output["Quantity"] = saved_and_loaded_model_output["Quantity"].astype(str)
        # Assert with pandas that loading saved result from previous function also worked.
        pd.testing.assert_frame_equal(saved_and_loaded_model_output,expected_multiple_prediction_df)
        
       