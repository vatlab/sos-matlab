function [repr] = sos_load_obj (filename)
    a = load(filename)
    repr = a.obj
