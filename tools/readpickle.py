import pickle
import os
from os import path


class save_file:
    pass

filepath = path.abspath(path.join( path.dirname( path.dirname(__file__) ), "save_data.pkl" ))


with open(filepath, "rb") as f:
    r = pickle.load(f).__dict__

def print_content(data, indent=0):
    spacer = "\t" * indent

    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                print("%s%s = {" % (spacer, k))
                print_content(v, indent + 1)
                print("%s}" % (spacer))
            else:
                print(f"{spacer}{k}:{v}")

    else:
        print(f"{spacer}{data}")

print_content(r)