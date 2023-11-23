from datetime import datetime

from termcolor import colored


def print_to_c(type, msg):
    """
    It prints a line, the current date and time, the input, another line, and a new line
    
    :param imp: The string to be printed
    """
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print(colored(dt_string, 'dark_grey'), end=' ')
    
    if type == "COMMAND":
        print(colored(type + " ", 'cyan'), end=' ')
    elif type == "SYNC":
        print(colored(type + "    ", 'red'), end=' ')
    elif type == "EVENT":
        print(colored(type + "   ", 'yellow'), end=' ')
    elif type == "LOAD":
        print(colored(type + "    ", 'green'), end=' ')
    else:
        print(colored(type + "    ", 'blue'), end=' ')
    
    print(colored("discord.bot", 'magenta'), end=' ')
    print(colored(msg, 'white'))