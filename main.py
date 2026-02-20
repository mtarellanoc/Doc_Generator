# !/usr/bin/python3.10
import copy
import  sys, os, sympy, random, argparse
import pandas as pd
from fractions import Fraction
from General_Scripts.references import home_directory, default_user_dict, df_keyword, call_keyword, recpy, stoppy, playpy, playpy_sort, playpy_place, default_recpy_sort_dict, default_group_dict

os.system('clear')
# ------------------------------------------------------------------------------------------------
# Setting up both local and global dataframes
column_names = ["name", "active_values", "active_ordered", "archived_values", "archived_ordered"]

# global dataframe to store all variables
df_global = pd.DataFrame(columns=column_names)
df_global.set_index("name", inplace=True)

# local dataframe to store all variables
df_local = pd.DataFrame(columns=column_names)
df_local.set_index("name", inplace=True)
# ------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="provide a file from current directory to compile")

# Optional argument
parser.add_argument('--file', type=str, help='file name with extension .tex or .typ')

args = parser.parse_args()
file_name = ""
if args.file:
    if args.file in os.listdir('.'):  # if file exists
        if args.file.endswith('.tex') or args.file.endswith('.typ'):
            file_name = args.file

        else:  # if wrong extension or file not found
            print(f"{file_name} has wrong extension. Must be '.tex' or '.typ'.")
            sys.exit()
    else:
        print(f'{args.file} not found in {os.getcwd()}')
        sys.exit()

else: # finding most recent file ------------
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
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------

def string_cleaning (user_dict, str_body):
    """
    This function removes comments, and white space such as double spaces, line breaks and tabs

    :param str_body:
    :param user_dict:
    :return: str_body
    """
    comment_symbol = user_dict["comment_symbol"]
    lines = str_body.split(f"\n")
    str_body = ""

    for line in lines:
        str_body = f"{str_body}{line.split(comment_symbol)[0]} "

    while True:
        if "  " not in str_body and "\n" not in str_body and "\t" not in str_body:
            break

        str_body = str_body.replace("  ", " ", 1)
        str_body = str_body.replace("\t", " ", 1)

    str_body = str_body.strip()

    return str_body


def string_extract(user_dict, str_body, string_keyword):
    """
    This function extracts the container, cleans it up to remove line breaks and tabs,
    and also provides the original string that held the container.
    :param user_dict:
    :param str_body:
    :param string_keyword:
    :return: Tuple - A string representing the container, and the original string that held the container
    """

    os.system('clear')

    open_container = user_dict['open_container']
    close_container = user_dict['close_container']
    comment_symbol = user_dict["comment_symbol"]

    # Finds the input command within container and returns input and code to be replaced
    try:  # this will run only if string_keyword is anything but ""
        str_right = str_body.partition(string_keyword)[2]  # string after keyword
    except:
        str_right = str_body


    before_open_container = str_right.partition(open_container)[0]  # string between keyword and opening container

    after_open_container = str_right.partition(open_container)[2]  # string after opening container

    bool_stop = False
    count_open_containers = 1
    count_close_containers = 0

    string_list = after_open_container.split("\n")  # splitting string by line breaks to remove comments
    str_remove = ""  # original line

    for line in string_list:

        line_before_comments = line.partition(comment_symbol)[0]

        if close_container not in line_before_comments:  # if line has no closing container
            count_open_containers = line_before_comments.count(open_container) + count_open_containers
            str_remove = f"{str_remove}{line}\n"

        else:  # if line has closing container
            active_string = line
            while True:  # loop in the event that multiple closing containers are in one line

                line_before_close = active_string.partition(close_container)[0]
                str_remove = f"{str_remove}{line_before_close}"

                count_close_containers = count_close_containers + 1
                count_open_containers = line_before_close.count(open_container) + count_open_containers

                # while loop ends if container found
                if count_close_containers == count_open_containers:
                    bool_stop = True # break line loop
                    break # break loop within single line

                else:
                    str_remove = f"{str_remove}{close_container}"

                active_string = active_string.partition(close_container)[2]

                if close_container not in active_string:  # while loop ends if end of line
                    str_remove = f"{str_remove}{active_string}\n"

                    break

            if bool_stop:
                break

    container = string_cleaning(user_dict, str_remove)

    str_remove = f"{string_keyword}{before_open_container}{open_container}{str_remove}{close_container}"

    return container, str_remove


def string_partitioning_single_layer(user_dict, str_args):
    """
    Takes a string and partitions it into arguments based on a pre-defined delimiter
    :param user_dict:
    :param str_args:
    :return: List of arguments
    """

    delimiter = user_dict['delimiter']
    opening_c = user_dict['open_container']
    closing_c = user_dict['close_container']

    arguments_list = []
    active_str = str_args
    while True: # loop for every complete argument found

        if active_str.strip() == "":
            break

        arg_str = ""
        while True:  # loop to build single argument
            arg_str = f"{arg_str}{active_str.partition(delimiter)[0]}"

            active_str = active_str.partition(delimiter)[2]
            if arg_str.count(opening_c) == arg_str.count(closing_c):
                arguments_list.append(arg_str.strip())
                break
            else:
                arg_str = f"{arg_str}{delimiter}"

    return arguments_list


def user_dict_and_container (str_body, keyword):
    """
    Identifies user_dict values and container
    :param str_body:
    :param keyword:
    :return: tuple:
            string to remove after keyword and before container,
            arguments within container,
            user_dict
    """
    active_region = str_body
    str_remove = f"{keyword}"

    # Default settings for user_dict
    user_dict = copy.deepcopy(default_user_dict)

    # modifying user_dict and identifying str_remove-------------------------------------------
    while True:

        # partitioning only the content between keyword and open_container
        active_argument = active_region.partition(keyword)[2].partition(f" {user_dict['open_container']}")[0]

        # removing leading and trailing white space, then separating arguments using space as the delimiter
        active_argument = active_argument.strip().partition(" ")[0]

        # removing this argument from active region
        active_region = active_region.replace(active_argument, "", 1)

        # if there is nothing inside left
        if len(active_argument) == 0:
            break

        if "=" not in active_argument:
            continue
        else:
            name = active_argument.split("=")[0]
            value = active_argument.split("=")[1]
            if name in user_dict.keys():
                user_dict[name] = value
            else:
                print(f"Error: -{name}- is not found in user_dict.")

    # prepping str_body to obtain container-------------
    # removing custom dictionary def's
    open_c = user_dict['open_container']
    keyword_to_open_container = f'{keyword}{str_body.partition(keyword)[2].partition(f" {open_c}")[0]}'

    str_body_with_no_user_dict = str_body.replace(keyword_to_open_container, f"{keyword}", 1)


    container, str_remove_no_dict = string_extract(user_dict, str_body_with_no_user_dict, keyword )


    str_remove = str_remove_no_dict.replace(keyword, keyword_to_open_container,1)

    return str_remove, container, user_dict


def rand (user_dict, min_range = 1, max_range = 10, value_type = "int", weights = "[]", amount = 1):
    """
    This will randomly generate a list of values within range in either integer, decimal or fraction format
    :param user_dict:
    :param min_range:
    :param max_range:
    :param value_type:
    :param weights:
    :param amount:
    :return: list of values
    """
    open_c = user_dict['open_container']
    close_c = user_dict['close_container']
    delimiter = user_dict['delimiter']
    amount = int(amount)
    list_values = []
    weights = weights[len(open_c):-len(close_c)] # removing opening and closing container

    # if value_type is int or decimal-----------------------------------------------------------
    # ------------------------------------------------------------------------------------------
    if value_type == "int" or value_type.split(user_dict['open_container'])[0].strip() == "decimal":
        # generating list of possible outcomes for value--------------------
        possible_values = [int(min_range)]  # first possible value
        while True:
            if value_type == "int":  # if value_type is 'int'
                value = possible_values[-1] + 1  # determines start of possible value

            else:  # if value_type is 'decimal[n]' where n is the amount of digits after decimal
                decimal = int(value_type.split(user_dict['open_container'])[1].split(user_dict['close_container'])[0])
                value = round(possible_values[-1] + 10 ** (-decimal), decimal)

            if value > int(max_range):  # terminates loop if exceeds max_range
                break
            else:
                possible_values.append(value)


        while True:  # removing all spaces in weights
            weights = weights.replace(" ", "")
            if " " not in weights:
                break

        # generating random values ----------------------------------------
        if weights == "":  # if no weights are given

            list_values = random.choices(possible_values, weights=None, k=amount)

        else:  # if weights are given

            # modifying weights to proper delimiter
            list_weights = weights.split(delimiter)

            str_weights = ""
            for weight in list_weights:
                if str_weights == "":
                    str_weights = weight
                else:
                    str_weights = f"{str_weights},{weight}"

            list_values = random.choices(possible_values, weights=(eval(str_weights)), k=amount)

    # if value_type is improper or mixed fraction-----------------------------------------------
    # ------------------------------------------------------------------------------------------
    else:
        container, original = string_extract(user_dict, value_type, "")
        denominator_min_max = string_partitioning_single_layer(user_dict, container)

        min_denominator = int(denominator_min_max[0])  # extracting min denominator from type
        max_denominator = int(denominator_min_max[1])  # extracting max denominator from type

        while True:  # loops until it reaches the amount of values
            if len(list_values) == amount:
                break

            while True:  # loops until fraction is within range

                whole_num = 0  # this will remain zero if value_type = 'improper'
                denominator = random.randint(min_denominator, max_denominator)  # this value is always positive

                if value_type.split(user_dict['open_container'])[0].strip() == "mixed":
                    whole_num = random.randint(int(min_range), int(max_range))  # this will allow min/max_range to be floats
                    numerator = random.randint(0, denominator - 1)

                else:
                    numerator = random.randint(int(min_range) * denominator, int(max_range) * denominator)

                if whole_num == 0 and float(min_range) < 0:
                    neg = random.randint(1, 2)
                    numerator = (-1) ** neg * numerator

                if whole_num < 0:  # This tests if value is negative--------------
                    float_value = float(whole_num - numerator / denominator)
                else:
                    float_value = float(whole_num + numerator / denominator)

                if float(min_range) <= float_value <= float(max_range):
                    break

            if numerator == 0:
                list_values.append(whole_num)
            elif whole_num == 0:
                list_values.append(f"{Fraction(numerator, denominator)}")
            else:
                list_values.append(f"{whole_num} {Fraction(numerator, denominator)}")

    return list_values


def arrange (user_dict, arrange_dict):

    open_c = user_dict['open_container']
    close_c = user_dict['close_container']
    delimiter = user_dict['delimiter']
    variable_call = user_dict['variable_call']

    # removes hashtag and any containers on the right
    variable = arrange_dict['variable'][1:].split(close_c)[0]
    order = arrange_dict['order'][1:].split(close_c)[0]

    # gathering list of values from variable
    variable_values = variable_list(variable)

    # gathering list of values from order
    order_values = variable_list(order)

    # checking lists meet requirements--------------------
    # ----------------------------------------------------
    if len(variable_values) != len(order_values):
        print(f"Error -arrange: {variable} and {order} don't have the same length")
        sys.exit()
    for value in list(range(len(order_values))):
        value = value + 1
        if value not in order_values:
            print(f"Error -arrange: {order} must be integers, with the smallest value set to 1")
            sys.exit()
    # ----------------------------------------------------
    # ----------------------------------------------------

    new_arrangement = []
    i = 0
    while i < len(variable_values):
        new_arrangement.append(variable_values[order_values[i]-1])
        i = i + 1

    return new_arrangement


def list_order (list_var):
    """
    Orders list of values, returns only list of rankings
    :param list_var:
    :return: ordered values
    """

    # Identify what type of sorting will take place
    # value or string
    #-----------------------------------------------
    string_bool = False # True if string value
    # is found
    for item in list_var:
        str_item = str(item)

        if " " in str_item:

            whole_n = str_item.split(" ")[0]
            proper_n = str_item.split(" ")[1]

            try:
                x = int(whole_n)
                y = eval(proper_n)

            except:
                string_bool = True
                break

        else:

            try:
                eval(str_item)

            except:
                string_bool = True
                break

    # building list_tuple, a list of tuples of the
    # form (item, item_value). item_value will be
    # used for sorting later
    # ---------------------------------------------
    list_tuple = []
    for item in list_var:
        str_item = str(item)  # convert to string to break characters
        if string_bool:  # If it is a string, store duplicate
            # item in tuple (item, item)
            list_tuple.append([item, item])
        else:  # if value
            if " " in str_item:  # if mixed number
                item_int = int(str_item.split(" ")[0])
                if item_int > 0:  # if positive value
                    item_frac = eval(str_item.split(" ")[1])
                else:  # if negative value
                    item_frac = eval(-str_item.split(" ")[1])
                item_value = item_int + item_frac  # compute value
                list_tuple.append([item, item_value])
            else:
                list_tuple.append([item, eval(str_item)])

    # sort list based on second element in tuple
    # ----------------------------------------------

    while True: # repeats entire sequence until values are ordered
        repeat_bool = False
        i = 1
        while i < len(list_tuple): # Goes through every item in list_tuple

            if list_tuple[i][1] < list_tuple[i-1][1]:
                repeat_bool = True
                temp = list_tuple[i]
                list_tuple[i] = list_tuple[i-1]
                list_tuple[i-1] = temp
            i = i + 1

        if not repeat_bool:  # breaks if list is ordered
            break

    # Using List_tuple[i][0] to create ordered_list
    # -----------------------------------------------
    o_list = []
    i = 0
    while i < len(list_var):
        o_list.append(list_tuple[i][0])
        i = i + 1

    return o_list


def computer_algebraic_system (user_dict, str_expression):
    open_c = user_dict['open_container']
    close_c = user_dict['close_container']
    if str_expression[0:len(open_c)] ==open_c and str_expression[-1:-len(close_c)-1:-1] == close_c:
        str_expression = str_expression[len(open_c):-len(close_c)]

    delimiter = user_dict['delimiter']
    str_expression = str(str_expression)  # changing the str_expression to a string variable

    if "verbatim" in str_expression:
        str_expression = str_expression.replace("verbatim ", "", 1).strip()
        return str_expression

    keywords = ["latex", "substitute", "solve", "simplify", 'expand', "factor", "log", "differentiate",
                "integrate", "if", "evaluate"]  # list of all keywords
    arguments = [0, 2, 1, 0, 0, 0, 1, 1, 1, 2, 0]  # amount of arguments needed in each keyword

    # IDENTIFIES THE ORDER OF KEYWORDS TO EXECUTE AND REMOVES THOSE KEYWORDS FROM str_expression VARIABLE
    str_expression_space_list = str_expression.split(" ")  # separating str_expression into list: delimeter " "
    execute_order_list = []  # prepping list to hold order of keywords to execute
    for keyword in str_expression_space_list:  # takes each keyword in str_expression (in the order as it appears) and
        # identifies the execute order
        i = 0  # counter which locates the keyword
        while i < len(keywords):  # condition to prevent i from going beyond the length of keywords
            if keyword == keywords[i]:  # conditional for checking if keyword in str_expression matches any of
                # the keywords
                str_expression = str_expression.replace(keyword, "", 1)  # redefines the str_expression variable with
                # one-less keyword
                execute_order_list.append(i)  # stores the location of keyword in list
                break  # terminates loop and moves on to the next term if keyword is found
            i = i + 1  # prevents infinite loop-sequence
        str_expression = str_expression.replace("  ", " ")  # removes any double spaces from str_expression

    # If keywords are found in str_expression
    if len(execute_order_list) != 0:
        str_expression_list = str_expression.split(delimiter)  # prepares str_expression by splitting into list
        # using predefined delimiter

        # TESTING IF CORRECT AMOUNT OF ARGUMENTS ARE GIVEN
        count_arguments = 0
        for item in execute_order_list:
            count_arguments = count_arguments + arguments[item]
        count_arguments = count_arguments + 1
        if len(str_expression_list) != count_arguments:
            print(f'Error: -Manipulation. There should be {count_arguments} in: {str_expression}')
            sys.exit()

        # EXECUTES EACH KEYWORD BASED ON THE ORDER IN WHICH APPEARS ON str_expression (LOOP)
        temp_removing = ""
        temp_execution = ""
        for execute in execute_order_list:
            if execute == 0:  # keyword: latex
                expression = str_expression_list[0]

                # execution name (must be the same for all cases
                temp_execution = str(
                    sympy.latex(sympy.parsing.sympy_parser.parse_expr(expression)))  # updates expression with
                # latex, stores as a new variable

                # cleaning str_expression
                temp_removing = str_expression_list[0]  # Determining parts to remove

            elif execute == 1:  # keyword: substitute
                expression = str_expression_list[0]  # separates str_expression as list with delimiter
                variable = str_expression_list[1].replace(" ", "")  # variable with no spaces
                substitution = str_expression_list[2]  # identifies replacement expression

                # execution name (must be the same for all cases
                temp_execution = expression.replace(variable, substitution)  # updates expression with
                # substitution, stores as a new variable

                # cleaning str_expression
                temp_removing = f"{str_expression_list[0]}{delimiter}{str_expression_list[1]}{delimiter}{str_expression_list[2]}"
                # Determining parts to remove

            elif execute == 2:  # keyword: solve

                expression = str_expression_list[0].replace(" ",
                                                            "")  # expression that will be set to 0 and solve for a variable
                variable = str_expression_list[1].replace(" ", "")  # defines the variable

                # execution name (must be the same for all cases
                temp_execution = str(sympy.solveset(expression, variable))  # updates expression with
                # solve, stores as a new variable

                # cleaning str_expression
                temp_removing = f"{str_expression_list[0]}{delimiter}{str_expression_list[1]}"
                # Determining parts to remove

            elif execute == 3:  # keyword: simplify

                expression = str_expression_list[0]

                # execution name (must be the same for all cases
                temp_execution = str(sympy.simplify(expression))  # updates expression with
                # simplify, stores as a new variable

                # cleaning str_expression
                temp_removing = f"{str_expression_list[0]}"
                # Determining parts to remove

            elif execute == 4:  # keyword: expand

                expression = str_expression_list[0]
                # execution name (must be the same for all cases
                temp_execution = str(sympy.expand(expression))  # updates expression with
                # expand, stores as a new variable

                # cleaning str_expression
                temp_removing = f"{str_expression_list[0]}"
                # Determining parts to remove

            elif execute == 5:  # keyword: factor

                expression = str_expression_list[0].replace(" ", "")

                # execution name (must be the same for all cases
                temp_execution = str(sympy.factor(expression))  # updates expression with
                # factor, stores as a new variable

                # cleaning str_expression
                temp_removing = f"{str_expression_list[0]}"
                # Determining parts to remove

            elif execute == 6:  # keyword: log

                value = str_expression_list[0]
                base = str_expression_list[1]

                # execution name (must be the same for all cases
                temp_execution = str(sympy.N(sympy.log(value) / sympy.log(base)))  # updates expression with
                # log, stores as a new variable

                # cleaning str_expression
                temp_removing = f"{str_expression_list[0]}{delimiter}{str_expression_list[1]}"
                # Determining parts to remove

            elif execute == 7:  # keyword: differentiate
                expression = str_expression_list[0]
                variable = str_expression_list[1]
                symbols = sympy.symbols(variable)

                # execution name (must be the same for all cases
                temp_execution = str(sympy.diff(expression, symbols))  # updates expression with
                # differentiate, stores as a new variable

                # cleaning str_expression
                temp_removing = f"{str_expression_list[0]}{delimiter}{str_expression_list[1]}"
                # Determining parts to remove

            elif execute == 8:  # keyword: integrate
                expression = str_expression_list[0]
                variable = str_expression_list[1]
                symbols = sympy.symbols(variable)

                # execution name (must be the same for all cases
                temp_execution = str(sympy.integrate(expression, symbols))  # updates expression with
                # integrate, stores as a new variable

                # cleaning str_expression
                temp_removing = f"{str_expression_list[0]}{delimiter}{str_expression_list[1]}"
                # Determining parts to remove

            elif execute == 9:  # keyword: if
                condition = str_expression_list[0]
                if_true = str_expression_list[1]
                if_false = str_expression_list[2]
                try:
                    if "==" in condition:
                        left_side = condition.split("==")[0]
                        right_side = condition.split("==")[1]
                        if eval(left_side) == eval(right_side):
                            temp_execution = if_true
                        else:
                            temp_execution = if_false
                    elif "!=" in condition:
                        left_side = condition.split("!=")[0]
                        right_side = condition.split("!=")[1]
                        if eval(left_side) != eval(right_side):
                            temp_execution = if_true
                        else:
                            temp_execution = if_false

                    elif ">=" in condition:
                        left_side = condition.split(">=")[0]
                        right_side = condition.split(">=")[1]
                        if eval(left_side) >= eval(right_side):
                            temp_execution = if_true
                        else:
                            temp_execution = if_false

                    elif "<=" in condition:
                        left_side = condition.split("<=")[0]
                        right_side = condition.split("<=")[1]
                        if eval(left_side) <= eval(right_side):
                            temp_execution = if_true
                        else:
                            temp_execution = if_false

                    elif ">" in condition:
                        left_side = condition.split(">")[0]
                        right_side = condition.split(">")[1]
                        if eval(left_side) > eval(right_side):
                            temp_execution = if_true
                        else:
                            temp_execution = if_false

                    elif "<" in condition:
                        left_side = condition.split("<")[0]
                        right_side = condition.split("<")[1]
                        if eval(left_side) < eval(right_side):
                            temp_execution = if_true
                        else:
                            temp_execution = if_false
                except:
                    print(f'Error -if statement: {str_expression}  is invalid.')
                    sys.exit()

                # cleaning str_expression
                temp_removing = f"{str_expression_list[0]}{delimiter}{str_expression_list[1]}{delimiter}{str_expression_list[2]}"
                # Determining parts to remove

            elif execute == 10:  # keyword: if evaluate

                expression = str_expression_list[0]
                # execution name (must be the same for all cases
                temp_execution = str(eval(expression))  # updates expression with
                # evaluate, stores as a new variable

                # cleaning str_expression
                temp_removing = f"{str_expression_list[0]}"
                # Determining parts to remove

            # UPDATES str_expression_LIST BEFORE NEXT ITERATION
            temp_str_expression = str_expression.replace(temp_removing, "", 1)  # Removing used parts
            # from str_expression
            str_expression = f"{temp_execution}{temp_str_expression}"  # prepares str_expression to be replaced with new
            # updated expression
            str_expression_list = str_expression.split(delimiter)  # prepares str_expression by splitting into list

    else:
        str_expression = str(eval(str_expression))

    return str_expression


def variable_list (variable):
    """
    Recalling list of values for a variable from dataframes.
    Variable should not have hashtag
    :param variable:
    :return:
    """
    if variable[0] == "!":
        variable = variable[1:] # removing ! and
        active_column = "active_ordered"
    else:
        active_column = "active_values"

    # gathering list of values from variable
    # ------------------------------------------------------------
    try:
        variable_values = df_local[active_column].loc[variable]
    except:
        try:
            variable_values = df_global[active_column].loc[variable]
        except:
            print(f"Error -variable_list: {variable} not found")
            sys.exit()

    return variable_values


def variable_value (user_dict, variable): # returns a single value
    """
    Callback to value of variable. must explicitly indicate which value in list to return
    Variable should not have hashtag
    :param user_dict:
    :param variable:
    :return: value
    """

    # --------Integrity test: checking for user error-------------------
    if user_dict['open_container'] not in variable:
        print(f"Error:Returns only single variables, not sets. see {variable}.")
        sys.exit()

    variable_name = variable.split(user_dict['open_container'])[0]
    index_value = int(variable.split(user_dict['open_container'])[1].split(user_dict['close_container'])[0])-1

    # Determining the set of values to look up
    list_of_values = variable_list(variable_name)
    # ---------------------------------------

    # checking to ensure value within container is within range
    if (int(index_value) > len(list_of_values)) or (int(index_value) < 0):
        print(f"Error: index value listed is not allowed. {variable}")
        sys.exit()
    # ------------------------------------------------------------------

    return str(list_of_values[index_value])


def update_string_with_variable_callback (user_dict, string):
    """
    Updates string with individual callback variable(s)
    :param user_dict:
    :param string:
    :return:
    """

    hashtag = user_dict["variable_call"]
    open_c = user_dict["open_container"]
    close_c = user_dict["close_container"]

    # replacing #call-backs with values
    while True:
        if hashtag not in string:
            break
        # determining string to replace:------------
        replace_str = f"{hashtag}{string.partition(hashtag)[2]}"  # level one, #...

        replace_str = f"{replace_str.partition(close_c)[0]}{close_c}"  #level two, # ... ]

        # determining the variable------------------
        # removing hashtag
        variable = replace_str[1:]
        # removing white space
        if " " in variable:
            while True:
                if " " not in variable:
                    break
                variable = variable.replace(" ", "")

        if open_c not in variable:
            print(f"Error: {variable} must explicitly indicate which value in list to call.")
            sys.exit()

        string = string.replace(replace_str, variable_value(user_dict,variable), 1)
    return string


def variable_extension (user_dict, expression):
    """
    Creates a list of values from callbacks in expression
    :param user_dict:
    :param expression:
    :return: list if values
    """

    delimiter = user_dict['delimiter']
    hashtag = user_dict['variable_call']
    open_c = user_dict["open_container"]
    close_c = user_dict["close_container"]

    # identify variable_list callbacks
    # ----------------------------------
    call_list_variables = []
    active_expression = expression
    while True:
        if hashtag in active_expression:

            after_hashtag = f"{hashtag}{active_expression.partition(hashtag)[2]}"
            variable = f"{after_hashtag.split(' ')[0].split(close_c)[0]}"

            if open_c not in variable:
                call_list_variables.append(variable)
            else:
                variable = f"{variable}{close_c}"
            active_expression = active_expression.partition(variable)[2]

        else:
            break

    # determining the loop count
    # ---------------------------
    if len(call_list_variables)>0:
        # if variable list were called
        n = len(variable_list(call_list_variables[0][1:]))
        for var in call_list_variables:
            if len(variable_list(var[1:])) < n:
                n = len(variable_list(var[1:]))
    else:
        # if no variable list were called
        n = 1


    # creating a list of expressions replacing the list_variables with
    # their respective values
    # ---------------------------
    i = 1
    list_new_expressions = []
    while i <= n:
        new_expression = expression
        for var in call_list_variables:
            if new_expression.partition(var)[2] != "":
                new_expression = new_expression.replace(f"{var} ", f"{var}[{i}] ", 1)
            else:
                new_expression = new_expression.replace(f"{var}", f"{var}[{i}] ", 1)
        list_new_expressions.append(new_expression)
        i = i + 1

    # updating list_new_expressions with calculated values
    # -------------------------------
    list_calc_expressions = []
    for exp in list_new_expressions:

        exp_callback = update_string_with_variable_callback(user_dict, exp)
        list_calc_expressions.append(computer_algebraic_system(user_dict, exp_callback))

    return list_calc_expressions


def record_variable (variable_name, values, local = False):
    ordered_values = list_order(values)

    # determining whether local or global will be used
    if local:
        active_dataframe = df_local
    else:
        active_dataframe = df_global
    # ---------------------------------------------
    # if new variable------------------------------
    if variable_name not in active_dataframe.index:
        # if new entries to dataframe

        active_dataframe.loc[variable_name] = [
            values, # active_values
            ordered_values, # active_ordered
            [values], # archived_values
            [ordered_values] # archived_ordered
        ]

    else:  # if not new variable-----------------
        archived_values = active_dataframe['archived_values'].loc[variable_name]
        archived_values.append(values)

        archived_ordered = active_dataframe['archived_ordered'].loc[variable_name]
        archived_ordered.append(ordered_values)

        active_dataframe.loc[variable_name] = [
            values,  # active_values
            ordered_values,  # active_ordered
            archived_values,
            archived_ordered
        ]

    return None


def load_variables (str_body):

    str_remove, container, user_dict= user_dict_and_container(str_body, df_keyword)
    arguments = string_partitioning_single_layer(user_dict, container)

    open_c = user_dict['open_container']
    close_c = user_dict['close_container']
    delimiter = user_dict['delimiter']

    # Each element will contain all the information of newly-defined variable
    global_variables = []
    variable_introduced = False  # this will prevent an argument appearing before 'variable name'

    # Filling local_variables and global_variables lists-----------------------------------
    for arg in arguments:
        # if 'global variable name', switches to global_variables list to append
        if arg.split("=")[0].strip() == "variable name":
            variable_introduced = True
            global_variables.append([arg])

        elif variable_introduced:  # adds all subsequent arguments for variables
            global_variables[-1].append(arg)

        else:
            print(f"error: {container} contains {arg} before declaring variable")
            sys.exit()

    # Reading each element and building variables-----------------------------------------
    for variable in global_variables:  # building each global variable:
        i = 1
        while True:
            # Terminates loop if conditions cannot be met
            #  ---------------------
            i = i + 1
            if i == 10000:
                print(f"Error:Loop exceeds 10000 iterations.\n {variable}")
                sys.exit()
            # ---------------------

            variable_dict = {
                "variable name": "",
                "allow repeat": "True",
                "cross referencing": 'combination',
                "add values": [],
                "local variable": "False"}

            for argument in variable:  # going through each argument in variable
                name = argument.partition("=")[0].strip()
                value = argument.partition("=")[2].strip()
                if name in variable_dict.keys() and name != "add values":  # condition to prevent new keys added
                    variable_dict[name] = value
                elif name != "add values":
                    print(f"Error: {argument} is unknown.")
                    sys.exit()

                # append option-------
                if name == "add values":
                    # identifying function ----------------------------------
                    function = value.split(open_c)[0].strip()
                    if function == "rand":  # rand option-------
                        # ----------------------------------------------------------------------------------------
                        # ----------------------------------------------------------------------------------------

                        rand_dict = {
                            "min": 1,
                            "max": 10,
                            "type": "int",
                            "weights": f"{open_c}{close_c}",
                            "amount": 1
                        }

                        # preparing rand arguments to be passed into rand function
                        str_partition, original_string = string_extract(user_dict, argument.partition("=")[2], "rand")
                        rand_arguments = string_partitioning_single_layer(user_dict, str_partition)

                        for rand_arg in rand_arguments:
                            rand_arg_name = rand_arg.partition('=')[0].strip()
                            rand_arg_value = rand_arg.partition('=')[2].strip()

                            if rand_arg_name not in rand_dict.keys():
                                print(f"Error: {rand_arg_name} is unknown.")
                                sys.exit()

                            else:
                                if rand_arg_name in ["min", "max", "amount"]:   # if min, max, amount
                                    # handles variable calls by replacing variable with value

                                    rand_arg_value = update_string_with_variable_callback (user_dict, rand_arg_value)
                                    # evaluates expressions
                                    try:
                                        rand_arg_value = eval(rand_arg_value)
                                    except:
                                        print(f"Error: {rand_arg} cannot be evaluated.")
                                        sys.exit()

                                elif rand_arg_name == "type":  # if type

                                    if "int" not in rand_arg_value:  # this only applies to decimal, improper and mixed
                                        #  Separating keyword from container expressions
                                        keyword = rand_arg_value.split(open_c)[0]
                                        container_str = rand_arg_value.partition(open_c)[2][:-len(close_c)]

                                        expressions = string_partitioning_single_layer(user_dict, container_str)

                                        # redefining the rand_arg_value variable
                                        rand_arg_value = f"{keyword}{open_c}"
                                        for exp in expressions:

                                            # if this is NOT the first exp in list of expressions, add delimiter
                                            if rand_arg_value[-1] != open_c:
                                                rand_arg_value = f"{rand_arg_value}{delimiter}"

                                            value = eval(update_string_with_variable_callback(user_dict, exp))
                                            rand_arg_value = f"{rand_arg_value}{value}"
                                        rand_arg_value = f"{rand_arg_value}{close_c}"

                                rand_dict[rand_arg_name] = rand_arg_value

                        variable_dict["add values"].extend(rand(user_dict,rand_dict['min'],rand_dict['max'],rand_dict['type'],rand_dict['weights'],rand_dict['amount']))

                    elif function == "arrange":  # arrange option ------
                        # ----------------------------------------------------------------------------------------
                        # ----------------------------------------------------------------------------------------
                        arrange_dict = {
                            "variable": "",
                            "order": "",
                        }

                        container = value[:-1].partition(open_c)[2].strip()

                        list_arguments = string_partitioning_single_layer(user_dict, container)

                        for arg in list_arguments:
                            name = arg.split("=")[0].strip()
                            value = arg.split("=")[1].strip()
                            if name in arrange_dict.keys():
                                arrange_dict[name] = value
                            else:
                                print(f"Error: {arg} is unknown.")
                        variable_dict["add values"].extend(arrange(user_dict, arrange_dict))
                    elif function == "extend": # extend option---

                        # identifies the expression within the extend keyword
                        # -------------------------------------------------------

                        expression = value.partition(open_c)[2][:-len(close_c)-1]
                        expression_list = string_partitioning_single_layer(user_dict, expression)
                        for expression in  expression_list:
                            variable_dict['add values'].extend(variable_extension(user_dict, expression))
                    else:
                        print(f"Error -rand: {function} is an unknown keyword")
                        sys.exit()
            # Check if conditions are met. if not, loop will repeat until satisfied
            # ---------------------------------------------------------------------
            # ---------------------------------------------------------------------
            # if repeat values are found, but not allowed, loop will start again

            if variable_dict['allow repeat'] == "False" and len(variable_dict['add values']) != len(set(variable_dict['add values'])):
                continue  # if repeat values are found, but not allowed, loop will start again

            if variable_dict['local variable'] == "True":  # if local variable

                # if new variable ----------------------------------------------------------------
                if variable_dict[
                    'variable name'] not in df_local.index:  # if variable name not found in dataframe, add
                    record_variable(variable_dict["variable name"], variable_dict["add values"], True)
                    break
                    #  ---------------------------------------------------------------------------

                else:  # if variable declared has been previously declared

                    # preparing list to compare new values to ------------------------------------------
                    if variable_dict["cross referencing"] == "combination":
                        compare_values = list_order(variable_dict["add values"])
                        archive_list = df_local['archived_ordered'].loc[variable_dict['variable name']]

                    elif variable_dict["cross referencing"] == "permutation":
                        compare_values = variable_dict["add values"]
                        archive_list = df_local['archived_values'].loc[variable_dict['variable name']]

                    else:  # if 'n/a' is the option under 'cross-referencing'
                        record_variable(variable_dict['variable name'], variable_dict['add values'], True)
                        break
                    # ----------------------------------------------------------------------------------

                    if compare_values not in archive_list:
                        record_variable(variable_dict['variable name'], variable_dict['add values'], True)
                        break

            else:  # if local variable is false
                # if new variable ----------------------------------------------------------------
                if variable_dict['variable name'] not in df_global.index:  # if variable name not found in dataframe, add
                    record_variable(variable_dict["variable name"], variable_dict["add values"])
                    break
                    #  ---------------------------------------------------------------------------

                else: # if variable declared has been previously declared
                    # preparing list to compare new values to ------------------------------------------
                    if variable_dict["cross referencing"] == "combination":
                        compare_values = list_order(variable_dict["add values"])
                        archive_list = df_global['archived_ordered'].loc[variable_dict['variable name']]

                    elif variable_dict["cross referencing"] == "permutation":
                        compare_values = variable_dict["add values"]
                        archive_list = df_global['archived_values'].loc[variable_dict['variable name']]

                    else: # if 'n/a' is the option under 'cross-referencing'
                        record_variable(variable_dict['variable name'], variable_dict['add values'])
                        break
                    # ----------------------------------------------------------------------------------

                    if compare_values not in archive_list:
                        record_variable(variable_dict['variable name'], variable_dict['add values'])
                        break
            # ---------------------------------------------------------------------
            # ---------------------------------------------------------------------


    df_local.drop(df_local.index, inplace=True)
    # last step, removing the df_keyword command from body
    str_body = str_body.replace(str_remove, "",1)

    return str_body


def fetch_variables (str_body):

    str_remove, container, user_dict = user_dict_and_container(str_body, call_keyword)

    arguments = string_partitioning_single_layer(user_dict, container)

    delimiter = user_dict['delimiter']
    open_c = user_dict['open_container']
    close_c = user_dict['close_container']
    var_call = user_dict['variable_call']


    # Gathering list of values
    # ------------------------------------
    list_values = []
    variable = arguments[0].strip()
    if open_c in arguments[0]:
        list_values.append(variable_value(user_dict, variable))
    else:
        list_values.extend(variable_list(variable))

    # Determining type of display
    # ------------------------------------
    if len(arguments) == 2:
        type = arguments[1].split(open_c)[0].strip()
    else:
        type = "basic"

    # Displaying values
    # ------------------------------------
    replacement_str = ""
    # if basic <--- Default
    if type == "basic":
        replacement_str = list_values[0]  # first entry
        i = 1
        while i < len(list_values):
            replacement_str = f"{replacement_str}, {list_values[i]}"
            i = i + 1

    # if tabular
    elif type == "tabular":
        tabular_dict = {
            'columns': '5',
            'style': '0',
            'left': 'False',
            'right': 'False',
            'top': 'False',
            'bottom': 'False',
            'horizontal': 'False',
            'vertical': 'False'
        }

        # Updating tabular_dict with user-defined values
        # -------------------------------
        tabular_raw_arguments = arguments[1].partition(open_c)[2][:-len(close_c)-1]
        tabular_list_arguments = string_partitioning_single_layer(user_dict, tabular_raw_arguments)
        for arg in tabular_list_arguments:
            keyword = arg.partition("=")[0].strip()
            value = arg.partition("=")[2].strip()
            if keyword not in tabular_dict.keys():
                print(f"Error -tabular: {keyword} not a keyword.")
                sys.exit()
            else:
                tabular_dict[keyword] = value
                if keyword == 'style':
                    # if keyword is style:
                    option = int(value)  # convert value to integer
                    # Top -------------------
                    if option % 2 == 1:
                        tabular_dict['top'] = 'True'
                    # Bottom ----------------
                    if (option // 2) % 2 == 1:
                        tabular_dict['bottom'] = 'True'
                    # Left ------------------
                    if (option // 4) % 2 == 1:
                        tabular_dict['left'] = 'True'
                    # Right -----------------
                    if (option // 8) % 2 == 1:
                        tabular_dict['right'] = 'True'
                    # Horizontal ------------
                    if (option // 16) % 2 == 1:
                        tabular_dict['horizontal'] = 'True'
                    # Vertical --------------
                    if (option // 32) % 2 == 1:
                        tabular_dict['vertical'] = 'True'

        # Determining the amount of rows and columns based on the list of
        # values and the columns set by user
        # -------------------------------
        columns = int(variable_extension(user_dict, tabular_dict['columns'])[0])
        rows = len(list_values)//columns
        if len(list_values) % columns != 0:
            rows = rows + 1
        cell_count = columns * rows

        # vertical bars (left, right, and middle)
        # -------------------------------
        if tabular_dict["left"] =="True":
            left = "|"
        else:
            left = ""
        if tabular_dict["vertical"] == "True":
            vertical = "|"
        else:
            vertical = ""
        if tabular_dict["right"] == "True":
            right = "|"
        else:
            right = ""

        # horizontal bars (top, bottom, and middle)
        # -------------------------------
        if tabular_dict["top"] == "True":
            top = r"\hline"
        else:
            top = ""
        if tabular_dict["bottom"] == "True":
            bottom = r"\hline"
        else:
            bottom = ""
        if tabular_dict["horizontal"] == "True":
            horizontal = r"\hline"
        else:
            horizontal = ""

        # tabular header
        # ------------------------------
        replacement_str = r"\begin{tabular}{"
        replacement_str = f"{replacement_str}{left}c"
        for i in range(1,columns):
            replacement_str = f"{replacement_str}{vertical}c"
        replacement_str = f"{replacement_str}{right}}}"

        # tabular body
        # ------------------------------
        replacement_str = f"{replacement_str}{top} "  # top
        i = 0
        while i < cell_count:
            new_row_bool = True
            for col in range(columns):
                if new_row_bool and i != 0:  # adding horizontal if not first value
                    replacement_str = f"{replacement_str}{horizontal} "
                if not new_row_bool:  # adding & if not first value in row
                    replacement_str = f"{replacement_str}&"
                if i < len(list_values):  # adding values
                    replacement_str = f"{replacement_str}{list_values[i]}"
                new_row_bool = False
                i = i + 1
            replacement_str = f"{replacement_str}\\\\"

        # closing tabular environment
        closing_tabular = r"\end{tabular}"
        replacement_str = f"{replacement_str}{bottom}{closing_tabular}"

    # last step, replacing the call_keyword command from body

    str_body = str_body.replace(str_remove, str(replacement_str), 1)

    return str_body


def load_fetch_variables(str_body):
    """
    reads str_body and stores variables with #df{...} and replaces #call{...} with stored variables
    :param str_body:
    :return: updated str_body
    """

    while True:


        if df_keyword not in str_body and call_keyword not in str_body:
            break

        if df_keyword in str_body and (call_keyword not in str_body.partition(df_keyword)[0]):  # run load_variables
            str_body = load_variables(str_body)

        else:  # run call_workflow
            str_body = fetch_variables(str_body)

    return str_body


def recpy_singlefile_search (playpy_code, file, str_body):
    """
    searches body for specific playpy_code in recpy. If found within file, returns playpy_code_bool = True
    return string to copy
    :param playpy_code:
    :param str_body:
    :return: typle:
        playpy_code_bool, str_copy
    """

    str_copy = ""
    rec_body = str_body
    while True: # looping through each recpy
        # searching within document for #recpy and #stoppy
        if str_body.count(stoppy) != str_body.count(recpy):
            print(f"Error -{recpy}: there is a mismatch of {recpy} to {stoppy} in {file}.")
            sys.exit()

        # break if #recpy not found

        if recpy not in rec_body:
            break

        # extracing recpy_code
        str_remove_rec, recpy_code, user_dict_recpy = user_dict_and_container(rec_body, recpy)

        if recpy_code == playpy_code: # if the recpy_code found in original document contains the requested code

            while True: # looping to determine the length of str_copy
                str_temp = rec_body.partition(str_remove_rec)[2].partition(stoppy)[0]
                str_remove_rec = f"{str_remove_rec}{str_temp}{stoppy}"

                if str_remove_rec.count(stoppy) == str_remove_rec.count(recpy):
                    str_copy = str_remove_rec
                    break

        rec_body = rec_body.replace(str_remove_rec, "", 1)

        if str_copy != "":
            break

    while True: # Removing all recpys and stoppys from str_copy
        loop_bool = False
        if recpy in str_copy:
            loop_bool = True
            str_remove_rec, recpy_code, user_dict_recpy = user_dict_and_container(str_copy, recpy)
            str_copy = str_copy.replace(str_remove_rec, "", 1)

        if stoppy in str_copy:
            loop_bool = True
            str_copy = str_copy.replace(stoppy, "", 1)

        if not loop_bool:
            break

    return str_copy


def recpy_general_search (playpy_code, str_body):

    str_copy = recpy_singlefile_search (playpy_code, file_name ,str_body)

    # Checking other files in active directory
    if str_copy == "" :
        # searching outside of document
        for file in os.listdir("."):
            if file.endswith(file_extension) and file != file_name and '--' not in file:
                with open(file, 'r') as rfile:
                    read_file = rfile.read()
                    str_copy = recpy_singlefile_search(playpy_code, file, read_file)

            # if file with code is found, break the loop
            if str_copy != "":
                break

    # searching files in template directory
    if str_copy == "":
        active_directory = os.getcwd()
        os.chdir(template_directory)
        for file in os.listdir("."):

            if file.endswith(file_extension) and '--' not in file:
                with open(file, 'r') as rfile:
                    read_file = rfile.read()
                    str_copy = recpy_singlefile_search(playpy_code, file, read_file)

            # if file with code is found, break the loop
            if str_copy != "":
                break

        os.chdir(active_directory)

    if str_copy == "":
        print(f"Error -playpy: no {recpy} found in {os.getcwd()} with code {playpy_code}")
        sys.exit()

    return str_copy


def load_playpy(str_body):

    active_body = str_body
    # loop for each #playpy found
    while True:
        if playpy not in active_body:
            break

        str_remove, playpy_code, user_dict_playpy =  user_dict_and_container(active_body, playpy)
        str_copy = recpy_general_search(playpy_code,active_body)

        active_body = active_body.replace(str_remove,str_copy, 1)

    # cleans up original document by removing #recpy  and stoppy from body
    # --------------------------------------------------------------------
    str_body = active_body
    while True:
        if recpy not in str_body:
            break

        str_remove_rec, container_rec, user_dict_recpy = user_dict_and_container(str_body, recpy)
        str_body = str_body.replace(str_remove_rec, "", 1)

    while True:
        if stoppy in str_body:
            str_body = str_body.replace(stoppy, "", 1)
        else:
            break

    return str_body


def load_sort_playpy(str_body):

    active_body = str_body

    if playpy_place in active_body.partition(playpy_sort)[0]:
        print(f"Error -playpy_sort: {playpy_place} is used before {playpy_sort}")
        sys.exit()

    while True: # reads each playpy_sort, one per iteration
        if playpy_sort not in active_body:
            break

        # Default settings recpy_sort_dict
        recpy_sort_dict = copy.deepcopy(default_recpy_sort_dict)

        str_remove, container, user_dict = user_dict_and_container(active_body, playpy_sort)

        open_container = user_dict["open_container"]
        len_open = len(open_container)

        close_container = user_dict["close_container"]
        len_close = len(close_container)

        delimiter = user_dict["delimiter"]

        active_body = active_body.replace(str_remove, "")

        # establish playpy.sort content
        parameters = string_partitioning_single_layer(user_dict,container)

        # list of dictionaries
        list_group_dictionaries = []

        # building list of recpy references *************
        for parameter in parameters: # reads each argument, one per iteration
            argument = parameter.split('=')[0].strip()
            value = parameter.partition('=')[2].strip()

            if argument == 'total amount':
                recpy_sort_dict['total amount'] = value

            elif argument == 'problem group':

                group_dict = copy.deepcopy(default_group_dict)
                group_parameters = string_cleaning(user_dict, value)

                # group_parameters cleaning------------------------------
                # removing opening container from string
                if group_parameters[0:len_open] == open_container:
                    group_parameters = group_parameters[len_open:]


                # removing opening container from string
                if group_parameters[-len_close:] == close_container:
                    group_parameters = group_parameters[:-len_close]

                group_parameters = group_parameters.strip()
                # group_parameters cleaning------------------------------

                arguments = string_partitioning_single_layer(user_dict, group_parameters)
                for arg in arguments:
                    dic = arg.split("=")[0].strip()
                    val = arg.split("=")[1].strip()

                    if dic in group_dict:
                        group_dict[dic] = val
                    else:
                        print(f"Error: {dic} is not a defined index in group_dic.\n must be {group_dict.keys()}")
                        sys.exit()

                # Determining Amount:
                if group_dict["amount"] == 0:
                    amount = rand(user_dict, group_dict["min"], group_dict["max"])[0]
                else:
                    amount = group_dict["amount"]

                list_group_dictionaries.append(group_dict)

            else:
                print(f'Argument within {playpy_sort} must match "total amount" or "problem group".')
                sys.exit()

        i = 1
        while True:
            count = 0
            for g_dic in list_group_dictionaries:
                if int(g_dic["amount"]) > 0:
                    g_dic["temp amount"] = int(g_dic["amount"])
                    count = count + g_dic["temp amount"]

                else:
                    g_dic["temp amount"] = rand(user_dict, g_dic["min"], g_dic["max"])[0]
                    count = count + g_dic["temp amount"]


            if count == int(recpy_sort_dict["total amount"]):
                break

            i = i + 1
            if i > 100000:
                print(f"Error:\n\n{list_group_dictionaries}\n\nexceeded iteration limit.")
                sys.exit()

        # creating list from strings
        for g_dic in list_group_dictionaries:
            # Converting string to type List:
            temp_list = g_dic["problem list"][len_open:]
            temp_list = temp_list[: -len_close]
            temp_list = string_partitioning_single_layer(user_dict, temp_list)

            # Randomizing sorting
            if g_dic["allow repeat"] == "True": # Random selection with replacement
                selected_items = random.choices(temp_list, k = int(g_dic["temp amount"]))
            else: # Random selection without replacement
                selected_items = random.sample(temp_list, int(g_dic["temp amount"]))

            #appending problems to Problem List
            recpy_sort_dict["problem list"].extend(selected_items)

        randomize_list = random.sample(recpy_sort_dict["problem list"], int(recpy_sort_dict["total amount"]))

        for index, item  in enumerate(randomize_list, start=1):
            search_key = f"{playpy_place} {open_container}{index}{close_container}"
            active_body = active_body.replace(search_key, f"{playpy} {open_container}{item}{close_container}",1)

    str_body = active_body

    return str_body


def update_body (str_body, bool_load_sort_playpy = True, bool_load_playpy = True, bool_load_fetch_variables = True, bool_load_local_packages = True):

    print("-----------UPDATING BODY-TEXT -------------------")

    while True:
        if bool_load_sort_playpy:
            print("reading sort.playpy and place.playpy arguments:")
            str_body = load_sort_playpy(str_body)
            print("loading playpy.place complete!\n")

        if bool_load_playpy:
            print("loading playpy text:")
            str_body = load_playpy(str_body)
            print("loading playpy complete!\n")

        if playpy_sort not in str_body:
            break

    if bool_load_fetch_variables:
        print("reading #df and #call arguments:")
        str_body = load_fetch_variables(str_body)
        print("loading variables complete!\n")

    if bool_load_local_packages:
        print("loading local packages")
        str_body = load_local_packages(str_body)
        print("loading local packages complete!\n")

    return str_body


def main ():
    """
    Reads file, stores and fetch variables. Creates a new file with updated body,
    then compiles new file
    :return: None
    """

    with open(file_name, 'r') as rfile:
        read_file = rfile.read()

    read_file = update_body(read_file)

    new_file = f"{file_name.split('.')[0]}--Standalone.{file_name.split('.')[1]}"
    with open(new_file, 'w') as wfile:
        wfile.write(read_file)

    compile_file(new_file)
    os.rename(f'{os.getcwd()}/{new_file.split(".")[0]}.pdf', f'{os.getcwd()}/{new_file.split("--")[0]}.pdf ')

    os.system('clear')
    print(f"{file_name.split('.')[0]}.pdf Complete!")
    print("-------------------------------------------------")
    return None


if __name__ == "__main__":
    main()