# !/usr/bin/python3.10
import sys, os,argparse

from doc_gen import update_body, select_file

# ------------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="Choose either 'tex' or 'typ' as the required mode.")
parser.add_argument(
    "mode",
    choices=["tex", "typ"],
    help="Required mode. Must be either 'tex' or 'typ'."
)
args = parser.parse_args()
print(f"You selected mode: {args.mode}")
if args.mode == "tex":
    from Tex_Scripts.references import compile_file
elif args.mode == "typ":
    print("this mode is still in development.")
    sys.exit()
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------

file = select_file(".tex")
directory = os.getcwd()

with open(file, 'r') as rfile:
     file_body = rfile.read()

# uploading playpy_callbacks before changing directories
file_body = update_body(file_body, True,False,False, False, True)

# Indicating Number of duplicates to be made
# ------------------------------------------
# ------------------------------------------
while True:
    try:
        copies_int = int(input("State the number of versions to create (enter 0 to terminate): ") or 0)
        if copies_int == 0:
            sys.exit()
        break
    except:
        print("Invalid entry. Try again.")

# Creating/Updating Directory
# ------------------------------------------
# ------------------------------------------
directory_copies = file.split('.tex')[0]
directory_copies = f'{directory}/{directory_copies}/'
if os.path.exists(directory_copies):  # if directory already exists erase all contents
    print(f'Directory {directory_copies}\n Already exist')
    os.chdir(directory_copies)
    os.system("rm * -f")
    os.chdir(directory)
else:  # if directory does not exist, create a new folder and transfer
    print(f'\nCreating directory: {directory_copies}')
    os.mkdir(directory_copies)

# Generating versions and copying them to assessment directory
# ------------------------------------------
# ------------------------------------------
for i in range(1, copies_int + 1):

    file_new_body = update_body(file_body, False,True, True,True, False)
    os.chdir(directory_copies)

    new_file = file.replace('.tex', f'--V{i}.tex')
    with open(new_file, 'w') as wfile:
        wfile.write(file_new_body)
    compile_file(new_file)

    os.chdir(directory)