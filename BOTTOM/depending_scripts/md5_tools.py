import hashlib


def get_md5(_buffer):
    md5 = hashlib.md5()
    md5.update(_buffer)
    cfg_md5_str = md5.hexdigest()
    return cfg_md5_str

def get_md5_block(_buffer):
    md5 = hashlib.md5()
    md5.update(_buffer)
    cfg_md5_str = md5.hexdigest()
    return cfg_md5_str

def get_file_md5(_file):
    fd = open(_file,"rb")
    md5 = hashlib.md5()
    while True:
        co = fd.read(1024)
        if not co:
            break
        else:
            md5.update(co)
    fd.close()
    cfg_md5_str = md5.hexdigest()
    #print "get_file_md5>>cfg_md5_str",cfg_md5_str
    return cfg_md5_str