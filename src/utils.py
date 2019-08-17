import tomlkit as toml

def write_config(toml_data, file_path):
    try:
        file = open(file_path, "w")
    except OSError as exc:
        logger.exception(f"Error with {file_path}:", exc_info=True)
        raise
    else:
        try:
            file.write(toml_data)
        except Exception as error:
            logger.exception("", exc_info=True)
            raise
        file.close()


def read_config(toml_path):
    toml_data = {}
    try:
        file = open(toml_path, "r")
    except FileNotFoundError:
        logger.exception("Error:", exc_info=True)
        raise
    else:
        try:
            toml_data = toml.parse(file.read())
        except Exception as error:
            logger.exception("", exc_info=True)
            raise
        file.close()

    return toml_data
