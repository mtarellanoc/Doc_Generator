# Document Generator
A flexible, keyword‑driven document generation engine for Python workflows
Doc_Generator is the successor to TeX_Test_Generator, redesigned to support a broader range of document types, richer keyword logic, and fully reproducible workflows. It allows users to define structured prompts, templates, and content blocks using simple keyword files — then automatically compiles them into complete documents.

### main function
*main.py* is the main script in this repository, as most of its defined functions are required for *versions.py* and *importpy.py*. 

When script is run directly, it will read the most recently updated **.tex** or **.typ** file in the current directory, and searches for the following keywords within the document:

- [#df](#df_details)  
    *#df*, short for datafame, is the command that you will use to store randomly generated variables and expressions.

- [#call](#call_details)  
    The *#call* keyword is used to call on variables previously defined using *#df*.

- [#playpy](#playpy_details)  
    This keyword searches for a *#recpy* with the exact name (searches through initial document, then all files in directory if code not found) and pastes its contents in place of *#playpy*

- [#recpy](#recpy_details)  
    all contents between *#recpy* and *#stoppy* can be copied and pasted using *#playpy* or *importpy*.

- [#sort.playpy](#sort.playpy_details)  
    *recpy names* within *#sort.playpy* are randomly sorted, and are then called using *#place.playpy*

- [#place.playpy](#place.playpy_details)  
    *#place.playpy* takes integers as its arguments, from 1 up to the amount of of *recpy names* listed in the previously defined *#sort.playpy*


Once the document has been read in, python will create a new document, **--Standalone.tex*, taking the body of the original **.tex* file and modifying based on the keywords listed above.

This new document is then compiled it twice. Once it has done so, it will remove *.log*, *.aux*, and *.out* files generated when compiled.

### versions

This script takes *main.py* and runs it repeatedly until multiple versions of the document have been generated. 

### importpy

*#importpy* is similar to *#playpy*, in that the keyword searches for a *#recpy* with the exact name. However this script explicitly imports the new code directly on the most recently saved **.tex** or **.typ** file in the current directory.

## Keywords Examples <a id="keyword_details"></a>
During compilation, the generator scans the document for any defined keywords and their corresponding blocks (by default, bracketed sections). Each keyword triggers its associated action based on the contents of the block — whether that means inserting text, repeating structures, transforming values, or executing custom logic. After processing, the system removes both the keyword and its entire block from the source file, ensuring that only the resolved output appears in the final compiled document. Below is how to use these keywords.

* [#df](#df_details)
* [#call](#call_details)
* [#recpy](#recpy_details)
* [#playpy](#playpy_details)
* [#sort.playpy](#sort.playpy_details)
* [#place.playpy](#place.playpy_details) 


### #df<a id="df_details"></a>

```
#df open_container=[ close_container=} delimiter=, variable_call=# comment_symbol=%   [

    % -------------------------------------------------------------------------
    variable name = var1,

    allow repeat = True, % Available options: False, True
    cross referencing = combination,  % Available options: combination, permutation, na
    local variable = False, % if true, local variables are deleted when closing #df container

    % rand function -----
    add values = rand[
        min = 1,
        max = 10,
        type = int, % Available options:
            % int,
            % decimal[2],  # number of decimals
            % improper[2,8],  # the smallest denominator the largest denominator allowed
            % mixed[2,8],  % mixed will provide proper fractions if min =0, and max = 1
        weights = [], % if empty, then uniform dist. (Only applies to decimal and integer types)
        amount = 1 % only takes integers
    ],

    % extend function ---
    add values = extend[
        #varname,  % if entire variable is given, all values in variable will be added
        1,
        3,
        #varname[3]
    ],

    % arrange function --
    add values = arrange[
        variable = #varname,  % variable to rearrange
        order = #ordervariable % list of orders
    ],
]
```


### #call<a id="call_details"></a>

```
#call [
    var1,
    basic, % <-- default. Other option:
    tabular[
        columns = 5,

        style = 63, % Other options 0-63

        left = False,
        right = False,
        bottom = False,
        top = False,
        horizontal = False,
        vertical = False,
    ]
]
```

### #playpy<a id="playpy_details"></a>

### #recpy<a id="recpy_details"></a>

### #sort.playpy<a id="sort.playpy_details"></a>

### #place.playpy<a id="place.playpy_details"></a>
