#########################################################################
#                     SAHIL PROGRAMMING LANGUAGE                        #
#                    author : Abdulbasit Rubeiyya                       #
#########################################################################

#########################################################################
#                               IMPORTS                                 #
#########################################################################

import sahil
from colorama import Fore, Back, Style

#########################################################################
#                                MAIN                                   #
#########################################################################

while True:
    text = input(Fore.GREEN + 'sahil > ' + Style.RESET_ALL)    #output on terminal
    result, error = sahil.run('--', text)                               #1

    if error: print(error.as_string())
    elif result: print(result)
 
#########################################################################
#                               COMMENTS                                #
#########################################################################

# 1- we do not pass the filename(fn) because this is repl