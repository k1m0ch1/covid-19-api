from os import environ
import logging

_ = environ.get

logging.basicConfig(format='[%(asctime)s][%(levelname)s]  %(message)s ',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)
