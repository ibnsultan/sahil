#########################################################################
#                     SAHIL PROGRAMMING LANGUAGE                        #
#                    author : Abdulbasit Rubeiyya                       #
#########################################################################

def string_pointer(text, pos_start, pos_end):
    result = ''

    # Calculate indices
    idx_start = max(text.rfind('\n', 0, pos_start.idx), 0)
    idx_end = text.find('\n', idx_start + 1)
    if idx_end < 0: idx_end = len(text)
    
    # Generate each line
    line_count = pos_end.ln - pos_start.ln + 1
    for i in range(line_count):
        # Calculate line columns
        line = text[idx_start:idx_end]
        col_start = pos_start.col if i == 0 else 0
        col_end = pos_end.col if i == line_count - 1 else len(line) - 1

        # Append to result
        result += line + '\n'       #this helps to undeline the point where the erro has occured
        result += ' ' * col_start + '^' * (col_end - col_start)

        # Re-calculate indices
        idx_start = idx_end
        idx_end = text.find('\n', idx_start + 1)
        if idx_end < 0: idx_end = len(text)

    return result.replace('\t', '')

 
#########################################################################
#                               COMMENTS                                #
#                                                                       #
#########################################################################

#This file point where the error is in the program, it will print the entire line and annotate where the error on that line is . eg
'''
sahil > 4*6/8 886 78
sintaksia batili: Tokeni inayotarajiwa ni '+', '-', '*' au '/' : Faili --, mstari wa 1

4*6/8 886 78
      ^^^^^^        
'''