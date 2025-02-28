import os
import configparser
from config import DB_INSTANCES_BASE_PATH
from modules.utilities.logger import logger  # Import logger module

def read_instance_cnf(company, instance, appuser, appuserid):
    """
    Reads the .instance.cnf file for the specified company and instance.

    Args:
        company (str): The company name.
        instance (str): The instance name.
        appuser (str): The application user requesting the operation.
        appuserid (str): The application user ID requesting the operation.

    Returns:
        tuple: A tuple containing (user, host, port, password) read from the .instance.cnf file.
    
    Raises:
        FileNotFoundError: If the instance folder or the .instance.cnf file is not found.
        Exception: For other general errors.
    """
    try:
        # Construct the paths for the instance configuration
        #db_instance_path = os.path.join(DB_INSTANCES_BASE_PATH, company, "system", "db_instances")
        db_instance_path = os.path.join(DB_INSTANCES_BASE_PATH, instance)       
        appuser = appuser if appuser is not None else 'initial' 
        #instance_folder = os.path.join(db_instance_path, instance)
        logger.debug(f"{appuser} --> {__name__}: Looking for instance folder at {db_instance_path}")

        if not os.path.isdir(db_instance_path):
            logger.error(f"{appuser} --> {__name__}: Instance folder for '{instance}' not found at {db_instance_path}")
            raise FileNotFoundError(f"Instance folder for '{instance}' not found.")
        
        config_file_path = os.path.join(db_instance_path, "db_config.ini")
        logger.debug(f"{appuser} --> {__name__}: Looking for db_config.ini file at {config_file_path}")

        if not os.path.exists(config_file_path):
            logger.error(f"{appuser} --> {__name__}: db_config.ini file not found for '{instance}' at {config_file_path}")
            raise FileNotFoundError(f"db_config.ini file not found for '{instance}'.")

        # Read the configuration file
        config = configparser.ConfigParser()
        config.read(config_file_path)
        logger.debug(f"{appuser} --> {__name__}: Successfully read the db_config.ini file for '{instance}'")

        # Extract the configuration values
        user = config.get('database', 'user').strip()
        host = config.get('database', 'host').strip()
        port = config.getint('database', 'port')
        password = config.get('database', 'password').strip()

        logger.debug(f"{appuser} --> {__name__}: Retrieved db user={user}, host={host}, port={port}, password=****")
        
        return user, host, port, password

    except FileNotFoundError as e:
        logger.error(f"{appuser} --> {__name__}: File not found error: {str(e)}")
        raise FileNotFoundError(str(e))
    except Exception as e:
        logger.error(f"{appuser} --> {__name__}: Error reading instance configuration: {str(e)}")
        raise Exception(f"Error reading instance configuration: {str(e)}")
