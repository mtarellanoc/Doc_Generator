# !/usr/bin/python3.1
import os,sys
from main import recpy_general_search, user_dict_and_container
from General_Scripts.references import home_directory

# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------

file_name = ""

# finding most recent file ------------
paths = [f"{home_directory}/"]
# list of subdirectories
i = 0
while True:
    active_directory = paths[i]

    if active_directory == "" or active_directory == " ":
        continue

    os.chdir(active_directory)
    for item in os.listdir('.'):
        if os.path.isdir(item):
            full_path = f"{active_directory}{item}/"
            paths.append(full_path)

    if i == len(paths) - 1:
        break

    i = i + 1

# identifying most recent file
# COMPARABLE VARIABLES-------------
most_recent_file = ["", "", -1]
# ---------------------------------

for dir in paths:
    os.chdir(dir)

    for file in os.listdir(dir):
        if (file.endswith('.tex') or file.endswith('.typ')) and "--" not in file:
            current_file = [dir, file, os.path.getmtime(file)]
            if current_file[2] >= most_recent_file[2]:
                most_recent_file = current_file

if most_recent_file[2] == -1:
    print(f"No file with extension 'tex' or 'typ' found in {home_directory}")
    sys.exit()

file_name = most_recent_file[1]
os.chdir(most_recent_file[0])
# -------------------------------------------

file_extension = ""
if file_name.endswith('.tex'):
    file_extension = '.tex'
    from Tex_Scripts.references import template_directory, compile_file, load_local_packages
else:
    file_extension = '.typ'
    from Typ_Scripts.references import template_directory, compile_file, load_local_packages

with open(file_name, 'r') as rfile:
    read_file = rfile.read()

importpy = '#importpy'

active_body = read_file
while True:
    if importpy in active_body:
        str_remove, container, user_dict = user_dict_and_container(active_body, importpy)

        import_str = recpy_general_search(container,active_body)

        active_body = active_body.replace(str_remove, import_str)

    else:
        break

with open(file_name, 'w') as wfile:
    wfile.write(active_body)
