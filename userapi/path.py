import os

def get_boxpath(dunderfile):
    dirpath = os.path.dirname(os.path.abspath(dunderfile))
    box_path = os.path.dirname(dirpath)
    return box_path