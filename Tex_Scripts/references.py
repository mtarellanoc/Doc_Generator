# !/usr/bin/python3.10
import os

# ------------------------------------------------------------------------------------------------
# ----------------------------------VARIABLES-----------------------------------------------------
template_directory = "/media/tovy/1TB/TeX_Templates/"
# ------------------------------------------------------------------------------------------------
def load_local_packages(str_body):
    """
    Updates .tex string, imports local packages into file.
    :param str_body:
    :return: str_body
    """

    active_string = str_body
    for file in os.listdir("."):
        if file.endswith(".sty"):
            file_name = file.replace(".sty", "")
            usepackage_file = f"\\usepackage{{{file_name}}}"

            if usepackage_file in active_string:

                package_file = open(file, "r")
                package_read = package_file.read()
                package_file.close()

                # clean up package file-- copies between \ProvidesPackage{  and \endinput
                package_content = package_read.partition(f'\\ProvidesPackage{{{file_name}}}')[2].partition(r"\endinput")[0]

                # Updates active_string
                active_string = active_string.replace(usepackage_file, package_content)

    active_directory = os.getcwd()
    os.chdir(template_directory)
    for file in os.listdir("."):
        if file.endswith(".sty"):
            file_name = file.replace(".sty", "")
            usepackage_file = f"\\usepackage{{{file_name}}}"

            if usepackage_file in active_string:

                package_file = open(file, "r")
                package_read = package_file.read()
                package_file.close()

                # clean up package file-- copies between \ProvidesPackage{  and \endinput
                package_content = package_read.partition(f'\\ProvidesPackage{{{file_name}}}')[2].partition(r"\endinput")[0]

                # Updates active_string
                active_string = active_string.replace(usepackage_file, package_content)

    os.chdir(active_directory)

    str_body = active_string

    return str_body


def compile_file (file):
    print(f"Compiling {file}...")
    os.system(f'pdflatex {file}')
    os.system(f'pdflatex {file}')

    rm_file_types = ["out", "log", "aux"]
    for type in rm_file_types:
        remove_file = f"{file.split('.')[0]}.{type}"
        if remove_file in os.listdir('.'):
            print(f"Removing {remove_file}")
            os.system(f"rm {remove_file}")
    return None

