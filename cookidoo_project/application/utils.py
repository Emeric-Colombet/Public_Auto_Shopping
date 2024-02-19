from datetime import datetime
import logging
import undetected_chromedriver as uc
from selenium import webdriver
import yaml
from yaml.loader import SafeLoader
import os

def get_date_with_underscore(): 
    date_with_underscore = datetime.today().strftime('%d_%m_%Y')
    return date_with_underscore

def generate_chrome_driver():
    logging.info("Initializing chrome option")
    chrome_options = webdriver.ChromeOptions()
    # TODO : Récupérer l'info du chemin du chromedriver dans une fichier d'environnement
    CHROMEDRIVER_PATH = 'data/chromedrivers/chromedriver'
    #WINDOW_SIZE = "1920,1080"
    WINDOW_SIZE = "1300,1000"
    chrome_options.add_argument("--window-size=%s" % read_safe_config_file()['window_size'])
    # The following command aims to load A personal Chrome profile, in order to get cookidoo's cookies.
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument(f"--user-data-dir={read_safe_config_file()['chrome_user_data_dir']}")
    chrome_options.add_argument(f"--profile-directory={read_safe_config_file()['chrome_user_data_profile']}")        
    driver = webdriver.Remote(
        command_executor='http://standalone-chrome:4444',
        options=chrome_options
    )
    #driver = uc.Chrome(
    #    driver_executable_path=CHROMEDRIVER_PATH,
    #    use_subprocess=True,options=chrome_options
    #    )
    driver.implicitly_wait(10)
    logging.debug("Chrome initialization ended")
    return driver

def read_safe_config_file() -> dict :
    """This function will load safely the config.yml file and return the whole dict."""
    # Open the file and load the file
    environment_dict = read_environment_variables()
    config_yml_path = environment_dict["CONFIG_PATH"]
    with open(config_yml_path) as f:
        config_dict = yaml.load(f, Loader=SafeLoader)
        return config_dict

def read_environment_variables()-> dict :
    """This function will load all environment variables, and add it to a dict"""
    env_variables = {}
    try : 
        config_path = os.environ["COOKIDOO_CONFIG_FILE_PATH"]
    except KeyError:
        logging.error("Can't load CONFIG_PATH FROM environment variable !! Be carreful, default value for config file path will be config.yml.")
        config_path = 'config.yml'
    env_variables["CONFIG_PATH"] = config_path
    return env_variables