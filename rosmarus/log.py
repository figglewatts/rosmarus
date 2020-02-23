import logging
import logging.config
from os import path
import sys
import yaml

from .application import Application

DEFAULT_CONFIG_FILENAME = "logging_config.yml"


def init(application: Application, config_filepath: str = None) -> None:
    if config_filepath is None:
        config_filepath = path.join(application.data_path,
                                    DEFAULT_CONFIG_FILENAME)
    with open(config_filepath, "r") as logging_config_file:
        logging_config = yaml.safe_load(logging_config_file)
        logging.config.dictConfig(logging_config)

    sys.excepthook = _exception_handler

    logging.info(f"Initialized logging for {application.name}")


def _exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.critical("Uncaught exception",
                     exc_info=(exc_type, exc_value, exc_traceback))
