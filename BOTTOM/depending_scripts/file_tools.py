
#-*-coding:utf-8*-
import os
import shutil
def del_file(filepath):
    """
    删除某一目录下的所有文件或文件夹
    :param filepath: 路径
    :return:
    """
    del_list = os.listdir(filepath)
    for f in del_list:
        file_path = os.path.join(filepath, f)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

def find_file_in_path(path, find_child=True,suffix=[]):
    ret = ""

    _limit = suffix
    _path = path
    if os.path.exists(_path):
        parents = os.listdir(_path)
    else:
        parents = []
        print "path not exists :", _path
    _out = []
    for parent in parents:
        tag = _path + "/" + parent
        if os.path.isdir(tag):
            if find_child:
                find_file_in_path(tag, find_child)
        else:
            suffix = tag.split(".")[-1]
            if (len(_limit) == 0):
                _out.append(tag)
            else:
                if (len(_limit) != 0) and (suffix in _limit):
                    _out.append(tag)

    return _out