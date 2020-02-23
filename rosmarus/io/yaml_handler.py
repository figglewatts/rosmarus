import logging

from marshmallow import Schema, ValidationError
import yaml

from .. import resources


def load_yaml(file_path: str, schema: Schema = None) -> object:
    with open(file_path, "r") as yaml_file:
        raw_yaml = yaml.safe_load(yaml_file)
        if schema is not None:
            try:
                return schema.load(raw_yaml)
            except ValidationError as err:
                _print_validation_err(err, file_path)
        else:
            return raw_yaml


def _print_validation_err(err: ValidationError, name: str) -> None:
    """Internal function used for printing a validation error in the Schema.

    Args:
        err (ValidationError): The error to log.
        name (str): A human-readable identifier for the Schema data source. 
            Like a filename.
    """
    # build up a string for each error
    log_str = []
    log_str.append(f"Error validating YAML file '{name}':")
    for field_name, err_msgs in err.messages.items():
        log_str.append(f"{field_name}: {err_msgs}")

    # print the joined up string
    logging.error(" ".join(log_str))


resources.register_type_handler("yaml", load_yaml)