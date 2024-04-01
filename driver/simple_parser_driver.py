#-*-coding:utf-8*-
import os,sys,json,re,glob,shutil
print "[RUNING CWD]",os.getcwd()
file = open("../driver/path.json","rb")
fileJson = json.load(file)
file.close()
#print fileJson
top = fileJson["top"]
top = "/../driver/"+top
cwd_path = os.path.abspath(sys.argv[0])
cwd = os.path.dirname(cwd_path)
print "[RUNING CWD]",cwd
sys.path.append(cwd+top+"/depending_scripts")

bash_title_arr = ["hevc_testenc_vc8000e","h264_testenc_vc8000e","jpeg_testenc_vc8000e"]
from test_list_tools import testlistManager
import file_tools
import cmdline_parser_new
from work_env_utils import WorkingInfoManager
from curr_run_info import curr_info

def get_test_manager(testlist):
    testlist_manager = testlistManager(testlist)
    testlist_manager.boot_testlist_env_status()
    #testlist_manager.get_out_change_testlist_flag()
    return testlist_manager

#把文件夹中所有满足后缀的文件当作testlist中的case
def gen_testlist_from_folder(folder_path,testlist_path):
    files = file_tools.find_file_in_path(path=folder_path, find_child=False,suffix=["yuv"])
    if not os.path.exists(os.path.dirname(testlist_path)):
        print "error...check the dir::",os.path.dirname(testlist_path)
    f = open(testlist_path,"w")
    for file in files:
        file = file.rstrip().strip("\n")
        re.sub(r'\\',"/",file)
        file += "\n"
        f.write(file)
    f.close()

def gen_curr_info(cwd):
    _curr_info = curr_info(dir=cwd,platform="REF_C",bash_id=0)
    setattr(glob,"curr_info",_curr_info)
    _curr_info.gen_curr_workInfo()

def GET_INPUT_FROM_GLOBAL():
    curr_info = getattr(glob, "curr_info")
    curr_env_path = curr_info.get_curr_env_path()
    inputfile = curr_env_path + "/src/input.txt"
    f = open(inputfile,"r")
    lines = f.readlines()
    f.close()
    _lines = []
    for l in lines:
        if l.strip("\n").rstrip() == "":
            pass
        else:
            _lines.append(l.strip("\n").rstrip())
    return _lines

def BOOT_TESTCASE(folder_path):
    curr_info = getattr(glob, "curr_info")
    curr_env_path = curr_info.get_curr_env_path()
    out_path = curr_env_path+"/testlist.txt"
    gen_testlist_from_folder(folder_path,out_path)
    return get_test_manager(out_path)


def ModifyDefaultCfg(workingInfoObj,yuv_path,suffix):
    curr_info = getattr(glob, "curr_info")
    curr_env_path = curr_info.get_curr_env_path()
    workspacepath = curr_env_path
    #得到codec_id
    org_cfg_dir = workspacepath+"/src"
    org_cfg_path = ''.join ((org_cfg_dir,'/tag.cfg'))

    cmdline = parse_cfg_ret_cmdline(cwd,curr_env_path,workingInfoObj,org_cfg_path,yuv_path,suffix)
    cfgFileName = getattr(glob,"curr_cfg_name")
    #curr_id = getattr(curr_info,"curr_id")
    #cmdline = change_cmdline_output_param(cmdline,curr_id)
    sh_dir = mkdir_in_workspace("sh")
    sh_file_name = sh_dir+"/"+cfgFileName + ".sh"
    sh_file = open(sh_file_name,"w")
    sh_file.write(cmdline)
    sh_file.close()

    param = {
        "sh_file_name":sh_file_name,
        "sh_bash_dir":cwd+"/"+sh_dir+"/../ref_c/"
    }
    return param

def UpdateCfg(workingInfoObj,testlist_manager):
    workingInfoObj.update_workingInfo_counter(1)
    if workingInfoObj.get_finish_flag():
        testlist_manager.finish_current_testfile()
def GET_WORKING_INFO():
    curr_info = getattr(glob, "curr_info")
    curr_env_path = curr_info.get_curr_env_path()
    jsonfile = curr_env_path + "/markInfo.json"
    db_path = curr_env_path + "/workingInfo.db"
    #rd_only = 0时仅仅用于打印目前环境可用的id
    workingInfoObj = WorkingInfoManager(persistentDBName=db_path)
    workingInfoObj.boot_WorkingInfo_with_json(jsonfile)
    workingInfoObj.boot_workingInfo_counter()#boot WorkingInfo持久化数据库
    return workingInfoObj
    # types_arr = workingInfoObj.mark
    # _workingInfo = workingInfoObj.get_counter_arr()

def CLEAN_ENV():
    curr_info = getattr(glob, "curr_info")
    curr_env_path = curr_info.get_curr_env_path()
    out_testcase_path = curr_env_path + "/testlist.txt"
    os.remove(out_testcase_path)
    rmdir_in_workspace(curr_env_path,"bs")
    rmdir_in_workspace(curr_env_path,"cfg")
    rmdir_in_workspace(curr_env_path, "sh")


def mkdir_in_workspace(cwd,type):
    p = cwd + "/" + type
    #print p
    if not os.path.exists(p):
        os.mkdir(p)
    return p

def rmdir_in_workspace(cwd,type):
    p = cwd + "/" + type
    #print p
    if os.path.exists(p):
        shutil.rmtree(p)

def parse_cfg_ret_cmdline( cwd ,curr_env_path,workingInfoObj,org_cfg_path, _path_dic,suffix):
    mark_param = workingInfoObj.mark
    # get workingInfo
    workingInfo = workingInfoObj.get_counter_arr()
    param = workingInfo
    _marknum = param[0]
    _cfgnum = param[1]
    _curr_time = param[2]
    # print "debug >>> _marknum:  " + str(_marknum)
    # print "debug >>> _cfgnum   :  " + str(_cfgnum)

    # gen name
    yuv_path = _path_dic["org"]

    yuv_name = yuv_path.split("/")[-1]
    cfg_desc = str(workingInfoObj.get_mark_type()) + "_" + str(workingInfoObj.get_mark_type_turn_param())

    cfgFileName = ''.join((yuv_name.split('.')[0], '_', cfg_desc, '.cfg'))
    cfgFileName = re.sub(r"\s{1,}", "", cfgFileName)
    setattr(glob, "curr_cfg_name", cfgFileName)

    print "[OUTPUT INFO]cfgFileName >>> " + cfgFileName
    bs_suffix = "." + suffix
    bsname = cfgFileName.split(".")[0]
    bsname = re.sub(r'\s{1,}', "", bsname).rstrip()
    # if re.search(r"nv12",yuv_path) != None:
    #     bsname = "nv12_"+bsname
    # elif re.search(r"yv12",yuv_path) != None:
    #     bsname = "yv12_"+bsname

    # gen path
    cfg_dir = mkdir_in_workspace(curr_env_path,"cfg")
    #bs_dir = mkdir_in_workspace(curr_env_path,"bs")

    dst_cfg_path = cfg_dir+"/"+cfgFileName
    # print "org_cfg_path",org_cfg_path

    sys.path.append(curr_env_path + "/autotest_config_scripts")
    import gen_testlist

    case_info_dict = gen_testlist.gen_case_info_dict( _path_dic)
    setattr(glob, "case_info_dict", case_info_dict)

    # 修改org.cfg生成tag.cfg
    changeCFG(org_cfg_path,
              dst_cfg_path,
              register_func=gen_testlist.register_funcs,
              kwargs={"workInfoManager": workingInfoObj,
                      "my_curr_info": getattr(glob, "curr_info"),
                      "case_info_dict": case_info_dict,
                      "bs_path": "out.bin"
                      })

    cmdline = get_cfg_cmdline(dst_cfg_path)
    if cmdline is None:
        print "[error] get_cfg_cmdline error..."
    return cmdline


def changeCFG( src_cfg, dest_cfg, register_func=None, kwargs=None):
    try:
        parser = cmdline_parser_new.cfg_processer()
        # 注册方法，该接口暴露给每个环境
        # 注册方法，根据每个环境中对case进行解析，根据需求添加参数进行解析
        if register_func:
            register_func(parser, **kwargs)
        parser.gen_new_cfg(src_cfg, dest_cfg)
    finally:
        del parser, register_func, kwargs


def get_cfg_cmdline(__cfg_path, bash_id=0):
    cmdline = None
    try:
        parser = cmdline_parser_new.cfg_processer()
        cmdline = parser.parse_cfg2args(cfg_path=__cfg_path, cmdline_title="./" +get_bash_dir())
    finally:
        del parser
        return cmdline

def get_bash_dir(bash_id = 0):
    return bash_title_arr[bash_id]


