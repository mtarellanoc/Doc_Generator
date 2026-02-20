# !/usr/bin/python3.10
import os

# ------------------------------------------------------------------------------------------------
# ----------------------------------VARIABLES-----------------------------------------------------
template_directory = "/media/tovy/1TB/Typ_Templates/"
# ------------------------------------------------------------------------------------------------
def load_local_packages(str_body):
    """
    Updates .typ string, imports local packages into file.
    :param str_body:
    :return: str_body
    """

    # in development

    return str_body


def compile_file (file):
    print(f"Compiling {file}...")
    os.system(f'typst compile {file}')
    return None

