from cookidoo_project.infrastructure.content_manager import ContentManager
from dataclasses import dataclass, field
import pandas as pd 
import spacy
from spacy.language import Language

@dataclass
class ModelWrapper():
    content_manager : ContentManager
    structured_shopping_list = pd.DataFrame(columns=["Raw","Quantity","Unit","Ingredient"])
    ner_model : Language = field(init=False)

    def __post_init__(self):
        self.ner_model = self.content_manager.load_model()

    def predict_shopping_list(self,raw_shopping_list : pd.DataFrame) -> pd.DataFrame:
        """This is the main function, it takes the"""
        doc_list = self.ner_labelisation_multiple_sentences(raw_shopping_list)
        for doc in doc_list : 
            quantity = None 
            unit = None
            food = None
            # Trick to have only one result for label QUANTITY or other, because sometimes it found multiple labels.
            for word in doc.ents:
                if quantity is None and word.label_ == "QUANTITY":
                    quantity = word.text
                if unit is None and word.label_ == "UNIT":
                    unit = word.text
                if food is None and word.label_ == "FOOD":
                    food = word.text
            data = {"Raw" : [str(doc)],
                   "Quantity" : [quantity],
                   "Unit" : [unit],
                   "Ingredient" : [food]}
            new_df_line = pd.DataFrame(data=data)
            self.structured_shopping_list = pd.concat([self.structured_shopping_list,new_df_line],ignore_index=True)
        # We automatically save the structured_shopping_list.
        self.content_manager.save_structured_shopping_list(structured_shopping_list=self.structured_shopping_list)
        return self.structured_shopping_list


    def ner_labelisation_multiple_sentences(self,sentences : pd.DataFrame): 
        raw_data_column_name = "raw_data_shopping_list"
        doc_list = []
        for sentence in sentences[raw_data_column_name] : 
            doc = self.ner_labelisation_one_sentence(sentence)
            doc_list.append(doc)
        return doc_list

    
    def ner_labelisation_one_sentence(self,sentence : str):
        doc = self.ner_model(sentence)
        return doc
    
