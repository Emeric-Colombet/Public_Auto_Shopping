# Auto_shopping

This project is an application who use Artificial Intelligence 🤖 (NER) to read your shopping list 📝 and automatically fill your supermarket drive cart 🛒.

## Functioning

Current developments work on Cookidoo application (Thermomix) for the shopping list and work on Carrefour for the supermarket drive.
Because we can't have access to the API's of those services, we will use scrapping on those sites.

### Program in action :

![alt text](https://github.com/Emeric-Colombet/Public_Auto_Shopping/blob/main/src/common/gifs/demo_scrapping.gif "Gif test")

#### Connection

When you launch the main.py file, it will make sure that you're correctly logged into those websites. (We currently can't auto log in because CloudFlare and Captcha security). So it will load a specified chrome profile, with cookies etc, and check if you are already connected; If not, it will leave you connect manually and save cookies.

#### Retrieve shopping list

After logging in, the program will open the selected Shopping List (currently Cookidoo), retrieve your ingredient list. (So, make sure that you have chosen your menus for the week). And it will save it and process it.

#### Processing

##### Artificial Intelligence

This part is our domain expertise. The app use an Artificial intelligence (Named Entity Recognition) to transform the raw ingredient list (For example : 100 g d'oignons coupés en rondelle) into standardised table with the following metrics isolated.

- Quantity (1,5,100...)
- Unit (g,L,c. à soupe, brins...)
- Ingredient (Oignons, tomates, viande hachée ...)

The AI was trained on some data labelised thanks to doccano. And trained to correctly identify metrics above. (For example, the AI recognize that for the sentence : 100 g d'oignons coupés en rondelle, 100 = Quantity, g = Unit, oignons = Ingredient, coupés en rondelle = Other).

##### Order history matching

Thanks to a previous work, we have stored all order history passed by the user. And we have saved his food habits. The application is now able to find the best matching ingredient given that your own habits.
For example : If ingredient is 'beurre' : The program will find that the most frequent purchase of beurre is 'Beurre demi-sel CARREFOUR CLASSIC'

#### Supermarket Ordering

This last program part takes as input the supermarket's ingredient name, and will search them on the drive, and add it to your cart.
At the end, you go on the supermarket's website to purchase your cart. Pay attention to the ingredients ordered, sometimes they are completly off the mark.

## Data organization

Firstly, all data are stored in files. (No Bdd). If you want to download data, please go to the [following link](https://drive.google.com/drive/folders/16_LjUpXnUGkGu5IatIlzI8XbvrEb_WcR?usp=share_link) and ask to access data.

Data files description (in french) :

- data
    - training_data

        - raw_data (les données txt issues de cookidoo)  
            - raw_data_1.txt  
            - raw_data_2.txt  
            - raw_data_3.txt
        - cleaned_raw_data (Les données propres (pas de token foireux comme : ½)) :
            - cleaned_raw_data.txt
        - labelised dataset (les données issues de doccano)
            - labelised_data.jsonl
            - labelised_data.spacy
            - labelised_data_validation.spacy
    - Shopping
        - Emeric_COLOMBET_id
            - Shopping_list_provider
                - Monsieur_Cuisine
                - Magimix_App
                - Cookidoo
                    - 19_04_2023_V0.txt (liste d'ingrédients a acheter)
            - Supermarket_provider
                - Carrefour
                    - History
                       - Drive_History
                           - 01_01_2021.html (Page internet commande historique)
                           - 01_02_2021.html
                           - ...
                       - Receipt_History
                           - 08_01_2021.txt (Récupération des tickets de caisse si carte de fidélité).
                           - ...
                       - Global_History
                           - carrefour_history.csv (Fichier contenant toutes les courses (Drive ou ticket de caisse) avec les noms drive des produits)
                - Auchan
                - Leclerc
                - Intermarché
            - Intermediate_data
                 - 19_04_2023_V0 (Commande effectuée)
                     - Structured_shopping_list.csv
                     - Supermarket_ingredient_to_order.csv (Export de tous les produits à acheter chez Carrefour pour la commande du jour).
            - Personal_information.yml
- models
    - model_v1
    - best_model

### Table Schema

#### Shopping list provider raw data

| raw_data_shopping_list |
| :--------- |
| 100 g de vin blanc sec |
| 300 g de riz spécial risotto |
| 100 g d'échalottes |

#### Structured shopping list provider

| Raw | Quantity | Unit | Ingredient |
| :--------- | :---------: | :---------: | :---------: |
| 100 g de vin blanc sec | 100 | g | vin blanc |
| 300 g de riz spécial risotto | 300 | g | riz spécial risotto |
| 100 g d'échalottes | 100 | g | échalotes |

#### Supermarket history global history

| Title | Description | Quantity | Price |
| :--------- | :---------: | :---------: | :---------: |
| Sauce pesto alla genovese basilic frais BARILLA | 190G | x1 | 1,52€ |
| Sauce Bolognaise BARILLA | 200G | x1 | 1,71€ |
| Sauces tomates double concentré PANZANI | les 3 boites de 70g | x2 | 3,70€ |

#### Structured shopping list matched with order history

*This file is not stored, it's a dynamic object, you can find it at Client class, match_structured_shopping_list_with_order_history method.*

| Raw | Quantity | Unit | Ingredient | Corresponding Carrefour Title |
| :--------- | :---------: | :---------: | :---------: | :---------: |
| 100 g de vin blanc sec | 100 | g | vin blanc | Vin blanc de table LA VILLAGEOISE |
| 300 g de riz spécial risotto | 300 | g | riz spécial risotto | Riz pour Risotto TAUREAU AILE |
| 100 g d'échalottes | 100 | g | échalotes | Echalotes de Bretagne agroécologie REFLETS DE FRANCE |

#### Auth.csv

Mettre un exemple de la table Auth.csv

## Technical Details

### Install requirements 
```bash
pip install -r requirements.txt
```

### Chrome

Chrome version : 111.0.5563.146
How to find chrome profile path : open Chrome, and in url, write chrome://version, and look at "chemin d'accès au profil".
Be carefull, if you have chrome already opened, the app will bug.

### Pytest

We have several tests to check program features.
To launch it write : `pytest cookidoo_project/test/`

## TODO list

Next features to develop.

- [x] Data analysis : Summary shopping
- [x] Containerisation (in order to run it into production) (Done on a private repo)
- [x] Notes_containerisation.md Add a front-end (streamlit)
  - [x] A button to launch principal program. (Done on another private branch)
  - [ ] A table to summarize raw ingredient in front of ordered ingredient. (It will allow user to find inconsistencies.)

- [x] CI-CD with github action. (Done on another private branch)

- [x] Add methods to manage customer (Add a new customer, remove it etc)

- [ ] Add a method to find not supermarket's ingredient name, but supermarket's ingredient id.

- [ ] Change history matching function to a better match.
