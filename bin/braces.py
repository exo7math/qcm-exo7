

#!/usr/bin/env python3

from re import *

# Find the first well-balanced string in brace
# Usage : find_braces(string)
# Example find_braces("Hello{ab{c}d}{fg}"") returns "ab{c}d", "Hello{", "}{fg}"


def find_braces(string):
    """return the first string inside a well-balanced expression with {}"""
    res = ""
    open_brace = False
    count = 0
    start = -1
    end = -1 

    for i in range(len(string)):

        s = string[i]

        # Not a first "{"
        if open_brace and s == "{":
             count += 1 

        # First "{"
        if not open_brace and s == "{":
            open_brace = True
            count += 1
            start = i

        if open_brace and s == "}":
             count += -1
             
        if open_brace and count==0:
            end = i
            break

    if not open_brace:
        return string, -1, -1

    return string[start+1:end], start+1, end

# Test 

# string = "\\feedback{$2^{10}=1024$}blabla"
# string = "rien du tout"
# string = "{au début{}}blaba"
# string = "blabla{à la fin {{}{}{}}xxx}"
# print(find_braces(string))



def find_command(command,string):
    trouve = search(command,string)
    if not trouve:
        return None

    c_start = trouve.start()
    find_res = find_braces(string[c_start:])
    c_end = c_start + find_res[2] + 1

    return string[c_start:c_end], c_start, c_end



# Test 

# string = r"coucou \feedback{$2^{10}=1024$}blabla"
# string = r"coucou {$2^{10}=1024$}blabla"
# command = "\\\\feedback"
# print(find_command(command,string))




