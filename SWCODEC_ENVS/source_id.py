#-*-coding:utf-8*-
import os
import sys
import time
import re
import datetime
cwd_path = os.path.abspath(sys.argv[0])
cwd = os.path.dirname(cwd_path)
#sys.path.insert(0, cwd + "/autotest_config_scripts")
sys.path.insert(0, cwd + "/../driver")

os.chdir(cwd)
cwd = re.sub(r"\\{1,}","/",cwd,0)

def find_files(_path):
    _limit = ["cfg"]
    _out = []
    _not = []
    parents = os.listdir(_path)
    for parent in parents:
        tag = _path + "/" + parent
        if os.path.isdir(tag):
            find_files(tag)
        elif tag == _path + "\\filelist.txt":
            continue
        else:
            houzhui = tag.split(".")[-1]
            if (len(_limit) == 0) and (len(_not) == 0):
                _out.append(tag)
            elif (parent=="id.cfg") or (parent == "tag.cfg") or (parent == "tmp.cfg"):
                    continue
            else:
                if (len(_limit) != 0) and (houzhui in _limit):
                    _out.append(tag)
                elif (len(_not) != 0) and (houzhui not in _not):
                    _out.append(tag)
    return _out
def important_param_md5(cfg_path):
    import hashlib
    md5 = hashlib.md5()
    #co = ""
    lines = open(cfg_path,"r").read()
    # for line in lines:
    #     if re.match("--input",line)!=None:
    #         print "[MD5-DELETE-LINE]",line
    #         continue
    #     if re.match("--output",line)!=None:
    #         print "[MD5-DELETE-LINE]",line
    #         continue
    #     co+=line
    md5.update(lines)
    cfg_md5_str = md5.hexdigest()
    return  cfg_md5_str

if __name__ == "__main__":
    import shutil
    path = cwd
    files = find_files(path)
    for file in files:
        id_str = important_param_md5(files)
        re_rule = r'(.+[/,\\]{1,})+([^@]{1,})+(@{1,})+(.{1,})+([.])+(.{1,})'
        aim_groups = re.match(re_rule,file)
        if aim_groups != None:
            dir = aim_groups.group(1)
            id_str_org = aim_groups.group(2)
            name = aim_groups.group(4)
            suffix = aim_groups.group(6)
            print "[ID_LIST]",id_str_org
            if id_str != id_str_org:
                new_path = dir+id_str+"@"+name+"."+suffix
                shutil.copyfile(file,new_path)
                os.rename(file,file+".org")
