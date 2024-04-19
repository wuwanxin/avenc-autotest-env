#-*-coding:utf-8*-
import os
import sys
import glob
import re
import time
import datetime
#import cfg
import json,shutil
import shutil
#print "[RUNING CWD]",os.getcwd()

#MAIN_FLAG_ADDR = cfg.FORMAT_ID_ADDR_START
#CHANGE_MAIN_TESTENV = cfg.CHANGE_MAIN_TESTENV
format_id_arr = [0]
codec_id = {
    "hevc":0,
}

cwd_path = os.path.abspath(sys.argv[0])
cwd = os.path.dirname(cwd_path)
print "[RUNING CWD]",cwd


#print dir()
#print __package__
#from depending_scripts import *
from ds_tools import ds_5_tools
from test_list_tools import testlistManager
from test_list_tools import testlistFileter
ds_5 = ds_5_tools()
import cmdline_parser_new
import work_env_utils
import worksapce_tools
import group_configuration_tool


codec = ["hevc","avc",'jpeg']
shell_dir = "shell/"
load_dir = "load/"
cmdline_title_arr = ["host"]
Persize = 0x9000000
#影响c环境下的命名的路径,除c模型以外的文件
paths = ["shell/readme"]
#自动化测试中的中间文件，该文件夹可以直接删除
tmp_dir = ".tmp"

def print_menu(options):
    for i, option in enumerate(options, start=1):
        print("{}) {}".format(i, option))

def get_user_choice(options):
    user_input = None
    while user_input not in range(1, len(options) + 1):
        try:
            user_input = int(raw_input("enter a num (1-{}): ".format(len(options))))
            if user_input not in range(1, len(options) + 1):
                print("error, input again")
        except ValueError:
            print("error, please input a number")
    return options[user_input - 1]

#该类后期需整理，目前暂时调通用
class curr_info:
    curr_cfg_name = ""
    curr_bash_path = ""
    def __init__(self,dir,platform,bash_id=0):
        self.dir = dir
        self.platform = platform
        self.bash_id = bash_id
        
        #获取当前运行的env
        #得到self.group
        file = open(self.dir+"/__group_confiuration__.json","rb")
        group = json.load(file)
        file.close()
        envs = group["envs"]
        options = []
        for env in envs:
            options.append(env["env_name"]+"$"+"hm")
        print_menu(options)
        selection = get_user_choice(options)

        s = selection.split("/")[-1].split("$")
        self.running_env_name = s[0]
        self.running_env_src_type = None


        self.wp_path = None
        self.sh_path = None

        if len(s)>1:
            self.running_env_src_type = s[1]            
        self.curr_env_path = self.dir + "/" + self.running_env_name

        self.group_cfg_obj = self.__gen_curr_group_cfg()
    def set_wp_path(self,path):
        self.wp_path = path
    def get_cur_envs_of_group_path(self):
        return self.dir 

    def get_curr_env_path(self):
        return self.curr_env_path
    def get_platform(self):
        return self.platform
    def get_curr_env_src_type(self):
        return self.running_env_src_type
    def save_bashFileName(self,FileName):
        dir = self.dir
        self.sh_path = FileName

        self.update_curr_status_db()

    def get_bashFileName(self):
        FileName = " "
        if self.sh_path:
            FileName = self.sh_path

        return FileName
    
    def __gen_curr_group_cfg(self):
        strs = self.dir.split("/")
        return group_configuration_tool.group_cfg(group_path=self.dir,env=self.running_env_name,json_file=self.dir+"/__group_confiuration__.json")

    def get_group_global_param(self):
        #print "global_param setting...",self.group_cfg_obj
        return getattr(self.group_cfg_obj,"global_param")
    def get_env_param(self):
        return getattr(self.group_cfg_obj,"env_param")
    def get_group_fix_mem(self):
        return getattr(self.group_cfg_obj,"fixed_mem_config")
    def get_id_ignore_marks(self):
        return getattr(self.group_cfg_obj,"id_ignore_marks")
    def gen_curr_workInfo(self,workspace):
        self.group_cfg_obj.gen_markInfo_jsonfile(workspace)
    def __init_curr_db_info(self):
        ret = {}
        ret["sh_path"] = self.get_bashFileName()
        ret["wp_path"] = self.wp_path
        return ret
    def get_wp_path(self):
        return self.wp_path

    def load_curr_info_from_db(self):
        p = self.__get_env_log_path()
        if not os.path.exists(p):
            return None
        fpOut = open(p, "r")

        curr = json.load(fpOut)
        self.wp_path = curr["wp_path"]
        self.sh_path = curr["sh_path"]
        return curr

    def __get_env_log_path(self):
        dir = self.dir
        run_dir = dir + "/.env_log"
        name = self.platform + "_" + str(self.bash_id) + ".json"
        p = run_dir + "/"+name
        if not os.path.exists(run_dir):
            os.mkdir(run_dir)
        return p
    def update_curr_status_db(self):

        fpOut = open(self.__get_env_log_path(), "w")

        json.dump(self.__init_curr_db_info(), fpOut)
        fpOut.close()

        
def workspace_naming(file_path):
    #set_space_name_suffix
    line = open(file_path,"r").readline().rstrip()
    print "[WORKSPACE SUFFIX]set suffix in file:",line
    #naming = str(datetime.datetime.now().strftime("%Y-%m-%d"))
    naming = str(datetime.datetime.now().strftime(line))
    print "[WORKSPACE SUFFIX FILE]get suffix:",naming

    return naming
def open_env(run_platform,set_cwd,set_space_name_suffix="",bash_id=0,print_only=0):

    print "======================================"
    print "run_platform:",run_platform
    print "set_cwd:",set_cwd
    print "set_space_name_suffix:",set_space_name_suffix
    print "======================================"
    #把环境的基本信息配置给当前的上下文运行环境
    my_curr_info = curr_info(dir=set_cwd,platform=run_platform,bash_id=bash_id)
    setattr(my_curr_info,"platform",run_platform)
    global_param = my_curr_info.get_group_global_param()
    setattr(glob,"global_param",global_param)
    env_param = my_curr_info.get_env_param()
    setattr(glob, "env_param", env_param)
    run_codec = env_param["codec"]
    setattr(glob, "run_codec", run_codec)
    
    #根据plaorm准备当前环境需要的命名
    run_codec_id = codec_id[run_codec]
    paths.append(shell_dir+cmdline_title_arr[run_codec_id])
    
    print "[REF_C_ID_IMPACT]",paths
    # **_run.py代码中的命名优先级最高
    if set_space_name_suffix=="":
        s = workspace_naming(set_cwd+"/workspace_naming.txt")
        ref_id = refc_detct_md5(paths)
        s=s + ("_ID["+ref_id+"]")
    set_cwd = my_curr_info.get_curr_env_path()
    
    #准备workspace
    WS_model = worksapce_tools.workspace_utils(cwd=set_cwd,platform=my_curr_info.running_env_name.upper()+"_"+run_platform+"_"+my_curr_info.get_curr_env_src_type().upper(),desc=run_codec,space_name_suffix=s)
    WS_model.open_workspace(src_suffix=my_curr_info.get_curr_env_src_type())
    my_curr_info.gen_curr_workInfo(workspace=WS_model.get_spacePath())
    setattr(WS_model, "curr", my_curr_info)
    my_curr_info.set_wp_path(WS_model.get_spacePath())
    my_curr_info.update_curr_status_db()
    
    if print_only:
        WS_model.gen_WorkingInfo_manager_instance_with_json("markInfo.json",1)
    else:
        test_mana = WS_model.gen_testlist_manager_instance()
        set_TestCaseFilter(WS_model, test_mana)
        WS_model.boot_testlist_manager_instance()
        WS_model.gen_WorkingInfo_manager_instance_with_json("markInfo.json")
        WS_model.boot_workspace()
    #拷贝ref c的文件到wp中
    if run_platform != "FPGA":
        ref_c_dir = WS_model.mkdir_in_workspace("run")
        
        run_log_dir = ref_c_dir
        print "run_log_dir::",run_log_dir
        for p in paths:
            pp = ref_c_dir + "/"+re.sub(r".+[\\,/]{1,}","",p)
            if not os.path.exists(pp):
                shutil.copyfile(p,pp)
        cmd = "cp -r " + set_cwd+"/model "+ref_c_dir
        os.system(cmd)
        cmd = "chmod -R -f 775 "+ref_c_dir
        print cmd
        os.system(cmd)


    return WS_model
    


def get_cmodel_path(ws_model):
    my_curr_info = getattr(ws_model, "curr")
    return my_curr_info.get_wp_path()+"/run"

def set_TestCaseFilter(ws_model,testlist_manager):
    my_curr_info = getattr(ws_model, "curr")
    print "set_TestCaseFilter::",my_curr_info.get_curr_env_path()
    sys.path.append(my_curr_info.get_curr_env_path() + "/autotest_config_scripts")
    import gen_testlist
    #kwargs与函数的参数需要一一对应
    # testcase参数不能改，该值内容会在filter中进行赋值操作
    # testcase以外的参数为自定义参数
    if (hasattr(gen_testlist, "FilterFunc") and hasattr(gen_testlist, "FilterFuncKwargs")):
        testlist_manager.set_filter(target=gen_testlist.FilterFunc, kwargs=gen_testlist.FilterFuncKwargs(my_curr_info))



def ModifyDefaultCfg(ws_model,yuv_path):
    workspacepath = ws_model.get_spacePath()
    my_curr_info = getattr(ws_model, "curr")
    #得到codec_id
    run_codec_id = codec_id[my_curr_info.get_env_param()["codec"]]
    org_cfg_path = workspacepath+"/src"
    org_cfg_path = ''.join ((workspacepath,'/priv_default.cfg'))
    cmdline = parse_cfg_ret_cmdline(ws_model,org_cfg_path,yuv_path,run_codec_id)
    curr_info  = getattr(ws_model,"curr")
    cfgFileName = getattr(curr_info,"curr_cfg_name")
    #curr_id = getattr(curr_info,"curr_id")
    #cmdline = change_cmdline_output_param(cmdline,curr_id)
    sh_dir = ws_model.mkdir_in_workspace("sh")
    sh_file_name = sh_dir+"/"+cfgFileName + ".sh"
    sh_file = open(sh_file_name,"w")
    sh_file.write(cmdline)
    sh_file.close()
    print "sh_file_name::",sh_file_name
    print "sh_bash_dir::",my_curr_info.get_wp_path()+"/run/"
    curr_info.save_bashFileName(sh_file_name)
    param = {
        "sh_file_name":sh_file_name,
        "sh_bash_dir":my_curr_info.get_wp_path()+"/run/"
    }
    return param

def UpdateCfg(ws_model):
    ws_model.update_curr_cmdline_wrap(1)


def RebootCfg(ws_model):
    ws_model.update_curr_cmdline_wrap(0)
#计算cfg中影响码流的配置的md5值
#对于vc8000e和j来说，只有input和output
def important_param_md5(cfg_path,desc=""):
    import hashlib
    md5 = hashlib.md5()
    co = ""
    f = open(cfg_path,"r")
    lines = f.readlines()
    f.close()
    for line in lines:
        if re.match(r"\s{0,}[^#]+::",line) == None:
            continue
        # elif re.match(r".+--input",line) != None:
        #     continue
        # elif re.match(r".+--output",line) != None:
        #     continue
        else:
            line = re.sub(r"\s{1,}","",line).strip("\n").strip("\t")+"\n"
            co+=line
    print "=============================txt=========================="
    print co
    print "=============================txt=========================="

    md5.update(co)
    cfg_md5_str = md5.hexdigest()
    #记录id内容
    os.remove(cfg_path)
    f = open(cfg_path,"w")
    f.write(co)
    f.close()


    #print cfg_md5_str
    return  cfg_md5_str

def refc_detct_md5(path_list=[]):
    import hashlib
    md5 = hashlib.md5()
    co = ""
    for p in path_list:
        lines = open(p,"rb").read()
        co+=lines
    md5.update(co)
    cfg_md5_str = md5.hexdigest()
    return  cfg_md5_str[0:8]
# def change_cmdline_output_param(cmdline,id):
#     outputname  = re.search(r"-o(.+?\s{1,})",cmdline).group(1).rstrip().strip(" ")
#     dir = re.match(r'(.+[/,\\]{1,})+(.{1,})',outputname).group(1)
#     name = re.match(r'(.+[/,\\]{1,})+(.{1,})',outputname).group(2)
#     outputname = dir+id+"@"+ name
#     print "[OUTPUT BITSTREAM]>>",outputname
#     cmdline = re.sub(r"-o(.+?\s{1,})", "-o "+outputname+" ", cmdline)
#     return cmdline

def parse_cfg_ret_cmdline(ws_model,org_cfg_path,_path_dic,codec_id):
    mark_param = ws_model.get_types_arr()
    _codec = codec[codec_id]

    #get workingInfo
    wim = ws_model.get_workingInfo_manager_instance()
    workingInfo = ws_model.get_work_info_counter()   
    param = workingInfo
    _marknum = param[0]
    _cfgnum = param[1]
    _curr_time = param[2]
    #print "debug >>> _marknum:  " + str(_marknum)
    #print "debug >>> _cfgnum   :  " + str(_cfgnum)
    
    #gen name
    yuv_path = _path_dic["org"]

    yuv_name = yuv_path.split("/")[-1]
    cfg_desc = str(wim.get_mark_type())+"_"+str(wim.get_mark_type_turn_param())+"_"+_codec

    cfgFileName = ''.join((yuv_name.split('.')[0],'_',cfg_desc,'.cfg'))
    cfgFileName = re.sub(r"\s{1,}","",cfgFileName)

    print "[OUTPUT INFO]cfgFileName >>> " + cfgFileName
    bs_suffix = "."+_codec
    bsname = cfgFileName.split(".")[0]
    bsname = re.sub(r'\s{1,}', "", bsname).rstrip()
    # if re.search(r"nv12",yuv_path) != None:
    #     bsname = "nv12_"+bsname
    # elif re.search(r"yv12",yuv_path) != None:
    #     bsname = "yv12_"+bsname
    
    #gen path
    cfg_dir = ws_model.mkdir_in_workspace("cfg")
    bs_dir = ws_model.mkdir_in_workspace("bs")
    
    #生成cfg的中间文件，后期需要为它重命名
    out_cfg_path = cfg_dir + "/out.cfg"
    tag_cfg_path = cfg_dir + "/tag.cfg"
    id_cfg_path = cfg_dir + "/id.cfg"
    
    #print "org_cfg_path",org_cfg_path
    
    my_curr_info = getattr(ws_model, "curr")

    id_ignore = my_curr_info.get_id_ignore_marks()
    
    sys.path.append(my_curr_info.get_curr_env_path() + "/autotest_config_scripts")
    

    import gen_testlist

    case_info_dict = gen_testlist.gen_case_info_dict(my_curr_info,_path_dic)

    setattr(glob, "case_info_dict", case_info_dict)
    
    #修改org.cfg生成tag.cfg
    changeCFG(ws_model,
              org_cfg_path,
              tag_cfg_path,
              register_func=gen_testlist.register_funcs,
              kwargs={"workInfoManager":wim,
                      "my_curr_info":my_curr_info,
                      "case_info_dict":case_info_dict,
                      "bs_path":"out.bin",
                      "codec":_codec})

    # 修改tag.cfg生成tag.cfg.id
    changeCFG(ws_model,
              tag_cfg_path,
              id_cfg_path,
              register_func=gen_testlist.register_id_func,
              kwargs={"case_info_dict": case_info_dict,
                      "id_ignore":id_ignore
                      })

    # 计算md5，并cfg的命名需要添加上其md5值
    # desc是描述作用,yuv的信息，去掉路径，只添加yuv的名称
    cfg_md5_str = important_param_md5(id_cfg_path, desc=yuv_name)
    cfgFileName = cfg_md5_str + "@" + cfgFileName
    cfgFileNameId = cfgFileName + ".id"
    # 添加 cfg io信息
    bs_path = bs_dir + "/" + bsname + "@" + cfg_md5_str + bs_suffix
    print "[OUTPUT INFO]bs_path >>> " + bs_path
    changeCFG(ws_model,
              tag_cfg_path,
              out_cfg_path,
              register_func=gen_testlist.register_io_func,
              kwargs={"case_info_dict": case_info_dict,
                      "bs_path": bs_path
                      })

    #把cfg name赋值，之后会取用
    setattr(my_curr_info,"curr_cfg_name",cfgFileName)
    setattr(my_curr_info,"curr_id",cfg_md5_str)
    dst_cfg_path = cfg_dir + "/"+cfgFileName
    dst_cfgId_path = cfg_dir + "/"+cfgFileNameId
    #os.rename(cfg_path,dst_cfg_path)

    shutil.copyfile(out_cfg_path,dst_cfg_path)
    shutil.copyfile(id_cfg_path,dst_cfgId_path)
    #os.remove(id_cfg_path)
    #os.remove(cfg_path)

    cmdline = get_cfg_cmdline(dst_cfg_path,codec_id)
    print "cmdline::",cmdline
    if cmdline is None:
        print "[error] get_cfg_cmdline error..."
    return cmdline

def changeCFG(ws_model,src_cfg,dest_cfg,register_func=None,kwargs=None):
    try:
        parser = cmdline_parser_new.cfg_processer()
        # 注册方法，该接口暴露给每个环境
        # 注册方法，根据每个环境中对case进行解析，根据需求添加参数进行解析
        if register_func:
            register_func(parser,**kwargs)
        parser.gen_new_cfg(src_cfg, dest_cfg)
    finally:
        del parser,register_func,kwargs

def get_cfg_cmdline(__cfg_path,codec_id):
    cmdline = None
    try:
        parser = cmdline_parser_new.cfg_processer()
        cmdline = parser.parse_cfg2args(cfg_path=__cfg_path, cmdline_title="./" + cmdline_title_arr[codec_id])
    finally:
        del parser
        return cmdline

#================fpga上文件load操作===================
def get_suffix(input_path):
    return input_path.split(".")[-1]

#对于此处的input文件必须是指定load地址的文件
def restore_input_fix_mem_file(ws_model,ds_path,input_path):
    _paths = []
    if isinstance(input_path,dict):
        if input_path.has_key("after_filter"):
            _paths.append(input_path["after_filter"])
        else:
            print "[error] dont have key::after_filter"
        if input_path.has_key("others"):
            for key,value in input_path["others"].items():
                _paths.append(value)
        else:
            print "[note] dont have key::others"
    else:
        _paths.append(input_path)
    my_curr_info = getattr(ws_model, "curr")
    fix_mems = my_curr_info.get_group_fix_mem()
    print "[restore_input_fix_mem_file] :: ",_paths
    for path in _paths:
        for fix_mem in fix_mems:
            if get_suffix(path) == fix_mem["suffix"]:
                if fix_mem["suffix"] == "yuv":
                    restore_big_file(ds_path,path,fix_mem["mem_base"])
                else:
                    restore_normal_file(ds_path,path,fix_mem["mem_base"])


def restore_big_file(ds_path,path,global_param_BASE_name):
    ds_5.restore_ds_file_path = ds_path+"/restoreBig.ds"
    _BASE = int(global_param_BASE_name,16)
    ds_5.streamBase = _BASE
    ds_5.TestSwitch_wenjiancaijie = 0
    #print ds_5.restore_ds_file_path
    ds_5.restore_big_file(path, Persize)
    ds_5.excute_ds_file(ds_5.restore_ds_file_path)
    #os.remove(ds_5.restore_ds_file_path)
    


def restore_normal_file(ds_path,filepath,global_param_BASE_name):
    restore_ds_file_path = ds_path+"/restoreNormal.ds"
    _BASE = int(global_param_BASE_name,16)
    co = "restore "+filepath+" binary "+hex(_BASE)
    #print co
    ds_file =  open(restore_ds_file_path,"w")
    ds_file.write(co)
    ds_file.close()
    ds_5.excute_ds_file(restore_ds_file_path)
    #os.remove(restore_ds_file_path)


##=====================================
#处理file
#通过交互固定地址交互 filename，filesize，然后把file放在指定的address上
def get_load_path():
    return cwd+"/"+load_dir
def __get_load_file_name(ds_path,LOAD_FILE_NAME_ADDR):
    tagpath = ''.join((ds_path,'/tag.txt'))
    #LOAD_FILE_NAME_ADDR_START = int(getattr(glob, "global_param")["LOAD_FILE_NAME_ADDR_START"],16)
    dump_file_param_size(ds_path,tagpath,LOAD_FILE_NAME_ADDR,48-2)
    tagfile = open(tagpath,"r")
    
    #!!这个file path是相对地址，在用绝对地址的环境时这个地方要修改一下
    file_path = tagfile.readline().rstrip()
    #print "file_path",file_path
    tagfile.close()
    file_path =  cwd+"/"+file_path
    os.remove(tagpath)
    return file_path
def __get_load_file_base(ds_path,LOAD_FILE_BASE_ADDR_START):
    import binascii
    tagpath = ''.join((ds_path,'/tag1.txt'))
    #LOAD_FILE_BASE_ADDR_START = int(getattr(glob, "global_param")["LOAD_FILE_BASE_ADDR_START"],16)
    dump_file_param_size(ds_path,tagpath,LOAD_FILE_BASE_ADDR_START,4-2)
    tagfile = open(tagpath,"r")
    base = binascii.b2a_hex(tagfile.read())
    base = int(str(base).decode('hex')[::-1].encode('hex_codec'),16)
    #print "base",hex(base)
    tagfile.close()
    os.remove(tagpath)
    return base

def restore_file(ds_path,LOAD_FILE_NAME_ADDR,LOAD_FILE_BASE_ADDR_START,LOAD_FILE_SIZE_ADDR_START):
    restore_ds_file_path = ds_path+"/restoreFile.ds"
    filepath = __get_load_file_name(ds_path,LOAD_FILE_NAME_ADDR)
    base = __get_load_file_base(ds_path,LOAD_FILE_BASE_ADDR_START)
    #LOAD_FILE_BASE_ADDR_START = int(getattr(glob, "global_param")["LOAD_FILE_BASE_ADDR_START"],16)
    #LOAD_FILE_SIZE_ADDR_START = int(getattr(glob, "global_param")["LOAD_FILE_SIZE_ADDR_START"],16)
    co = "restore "+filepath+" binary "+hex(base)
    #print co
    ds_file =  open(restore_ds_file_path,"w")
    ds_file.write(co)
    ds_file.close()
    ds_5.excute_ds_file(restore_ds_file_path)
    ds_5.excute_write_memory(fill_start_addr=LOAD_FILE_SIZE_ADDR_START,fill_size=4,value=os.path.getsize(filepath))
    
##=====================================
def dump_file_param_size(ds_path,output,BASE,SIZE):
    ds_5.dump_ds_file_path = ds_path+"/dump.ds"
    #print "dump_ds_file_path >>> ",ds_5.dump_ds_file_path
    ds_5.dump_file_param_size(output,BASE,SIZE)
    ds_5.excute_ds_file(ds_5.dump_ds_file_path)
    #os.remove(ds_5.dump_ds_file_path)

def dump_file_param_endaddr(ds_path,output,BASE,END_ADDR):
    ds_5.dump_ds_file_path = ds_path+"/dump.ds"
    #print "dump_ds_file_path >>> ",ds_5.dump_ds_file_path
    ds_5.dump_file_param_endaddr(output,BASE,END_ADDR)
    ds_5.excute_ds_file(ds_5.dump_ds_file_path)

def ec_continue():
    ec = ds_5.get_debugger_instance()
    ec.getExecutionService().resume()

#jpeg or hevc/avc ，通过修改ddr中flag的地址，代码会在ddr中去取
def boot_src_env(platform):
    print "platform:",platform
    if platform == "FPGA":
        global_param = getattr(glob, "global_param")
        MAIN_FLAG_ADDR = global_param["FORMAT_ID_ADDR_START"]
        MAIN_FLAG_ADDR = int(MAIN_FLAG_ADDR, 16)
        CHANGE_MAIN_TESTENV = global_param["CHANGE_MAIN_TESTENV"]
        CHANGE_MAIN_TESTENV = int(CHANGE_MAIN_TESTENV, 16)
        format_id = format_id_arr[codec_id[getattr(glob, "env_param")["codec"]]]
        ds_5.excute_write_memory(fill_start_addr=MAIN_FLAG_ADDR,fill_size=4,value=format_id)
        ds_5.excute_write_memory(fill_start_addr=CHANGE_MAIN_TESTENV,fill_size=4,value=0)
    elif platform == "REF_C":
        pass
#结束当前环境
def close_env(platform,run_bash):
    if platform == "FPGA":
        global_param = getattr(glob, "global_param")
        CHANGE_MAIN_TESTENV = int(global_param["CHANGE_MAIN_TESTENV"],16)
        env_manager = testlistManager(testlist_path=cwd+"/../envlist_fpga.txt")
        ds_5.excute_write_memory(fill_start_addr=CHANGE_MAIN_TESTENV,fill_size=4,value=1)
    elif platform == "REF_C":
        print "[CLOSE ENV]"+cwd+"/../envlist_refc_"+str(run_bash)+".txt"
        env_manager = testlistManager(testlist_path=cwd+"/../envlist_refc_"+str(run_bash)+".txt")
        env_manager.boot_testlist_env_status()
    else:
        print "[CLOSE ENV]"+cwd+"/../envlist_"+str(run_bash)+".txt"
        env_manager = testlistManager(testlist_path=cwd+"/../envlist_"+str(run_bash)+".txt")
        env_manager.boot_testlist_env_status()
    env = env_manager.get_current_testfile()
    env_manager.finish_current_testfile()
    
    
def load_cmdline(cmdline):
    ret = {}
    
    cos = cmdline.split(" ")
    title = cos[0]
    ret["title"] = title
    i = 1
    #print cos
    while i<len(cos)-1:
        #print "test1:::::",cos[i]
        #print "test2:::::",cos[i+1]
        if not re.match(r"^-",cos[i+1]):
            ret[cos[i]] = cos[i+1]
            #print ">>",cos[i],"=",cos[i+1]
            i=i+2
        else:
            ret[cos[i]] = "NULL"
            #print ">>",cos[i],"=NULL"
            i=i+1
    #print ret
    return ret



#======================================================================
#关于recon生成md5的内容
#其中会调用到底层的recon_check模块
#
def gen_my_recon_yuv_dict(recon_yuv_path,case_info_dic):
    sample_my_yuv_info = {
        "path":recon_yuv_path,
        "stride":int(case_info_dic["width"]),
        "width":int(case_info_dic["width"]),
        "height":int(case_info_dic["height"]),
        "frame_count":int(case_info_dic["framenum"]),
    }
    return sample_my_yuv_info


#param :: save_recon_yuv_flag   表示是否需要存下当前的recon yuv，若需要存储，可能会消耗大量内存，建议只在debug的时候开启
def do_recon_check(ws_model,platform,src_recon_path,output_name="deblock.yuv",save_recon_yuv_flag=0):
    if platform == "FPGA":
        pass
    else: 
        from recon_check import recon_check
        if hasattr(glob,"case_info_dict"):
            #my_yuv_info_dic的具体keys需要查询"gen_testlist.gen_case_info_dict()"
            #该接口是用户自己配置的
            my_case_info_dict = getattr(glob,"case_info_dict")
        else:
            print "[error]not set glob attr [case_info_dict],please check it ..."

        my_curr_info = getattr(ws_model, "curr")
        org_recon_yuv_path = src_recon_path
        
        if save_recon_yuv_flag:
            #在wp中创建recon文件夹存放recon数据
            recon_dir = ws_model.mkdir_in_workspace("recon")
            recon_yuv_path = recon_dir + "/" + output_name
            #拷贝recon数据
            shutil.copyfile(org_recon_yuv_path,recon_yuv_path)
            print "recon_yuv_path:",recon_yuv_path
            #time.sleep(10)
        else:
            recon_yuv_path = org_recon_yuv_path
        #md5 存放的位置可更换
        recon_md5_dir = ws_model.mkdir_in_workspace("recon")
        md5_recon_yuv_path = recon_md5_dir + "/" + output_name+".md5"
        print "[do_recon_check]set recon md5 file path:",md5_recon_yuv_path
        #time.sleep(10)
        recon_info_dic = gen_my_recon_yuv_dict(recon_yuv_path,my_case_info_dict)
        recon_check_obj = recon_check()
        
        recon_check_obj.INIT_RECON_ENV(recon_info_dic)
        inst = recon_check_obj.GET_MULTI_INSTANCE()
        #给inst设置output_path参数
        #若有该参数才会使用外部配置的输出地址，否则会使用默认地址
        #具体地址查看源码
        setattr(inst,"output_path",md5_recon_yuv_path)
        inst.proc()
        #释放内存
        del recon_check_obj