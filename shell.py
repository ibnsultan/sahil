#########################################################################
#                     SAHIL PROGRAMMING LANGUAGE                        #
#                    author : Abdulbasit Rubeiyya                       #
#########################################################################
import sahil

while True:
    text = input('sahil > ')    #output on terminal
    result, error = sahil.run('Ndani ya Faili hii', text)                          #1

    if error: print(error.as_string())
    else: print(result)
 
#########################################################################
#                               COMMENTS                                #
#                                                                       #
#########################################################################

#we do not pass the filename(fn) because this is repl