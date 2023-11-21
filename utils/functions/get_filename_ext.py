import os
import locale

def number_seprator(a):
    return format(a, ',d')


def get_filename_ext(filepath):
    name, ext = os.path.splitext(os.path.basename(filepath))
    return name, ext  
