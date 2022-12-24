import string
import random

def gen(_LENGTH):

    string_pool = string.ascii_letters + string.digits

    result = "" 
    for i in range(_LENGTH) :
        result += random.choice(string_pool)

    return result