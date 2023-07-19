import configparser
import logging


def init_config(config_file_path):
    """
    Initializes the configuration
    Args:
        config_file_path:str: Path to .ini configuration file
    """

    # asserting configuration file has the correct extension
    path = config_file_path.split('.')
    assert(path[len(path)-1] == 'ini')

    config = configparser.ConfigParser()
    config.read(config_file_path)
    return config

def get_logger(logger_file_path):
    """
    Creates a logging object and returns it
    Returns:
        logger:logging.Log: Log object
    """

    logger = logging.getLogger('InstaBotLogger')
    logger.setLevel(logging.DEBUG)
 
    # log file handler
    fh = logging.FileHandler(logger_file_path)
 
    # log format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
 
    logger.addHandler(fh)
    logger.addHandler(logging.StreamHandler())
    return logger