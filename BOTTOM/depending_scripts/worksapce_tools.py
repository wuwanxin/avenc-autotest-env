#!/usr/bin/env python 
#-*-coding:utf-8*-
import os
import sys
import glob
import re
import datetime
from work_env_utils import WorkingInfoManager
from test_list_tools import testlistManager
from shutil import copyfile
class workspace_utils:
    def __init__(self,cwd="",platform="REF_C",desc="hevc",space_name_suffix=""):
        #startTime = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.space_name_suffix = space_name_suffix
        if self.space_name_suffix=="":
            self.space_name_suffix = str(datetime.datetime.now().strftime("%Y-%m-%d"))
        self.cwd = cwd
        if cwd=="":
            self.cwd=os.getcwd()
        self.platform = platform
        self.spaceName = "WS_"+platform+"_"+str(self.space_name_suffix)
        print "[WORKSPACE]",self.spaceName
        self.spacePath = ''.join ( (cwd,"/",self.spaceName) )
        self.priv_testlist_path = self.spacePath+"/testlist_priv.txt"
        self.note_path = self.spacePath+ "/" +str(desc) +"_note.txt"
        self.desc = desc
        self.reset_wi_counter = 0
        self.change_testlist_flag = 0
        self.testlist_manager = NotImplemented
        self.workingInfoObj = NotImplemented
        #self.boot_workspace()

    def gen_testlist_manager_instance(self,size=0x40000000):
        self.testlist_manager = testlistManager(self.priv_testlist_path,size)

        return self.testlist_manager

    def get_testlist_manager_instance(self):
        if self.testlist_manager:
            return self.testlist_manager
        else:
            print "[error]please gen_testlist_manager_instance first..."

    def boot_testlist_manager_instance(self):
        self.testlist_manager.boot_testlist_env_status()
        self.change_testlist_flag = self.testlist_manager.get_switch_testfile_flag()


    def get_out_change_testlist_flag(self):
        ret = self.testlist_manager.get_switch_testfile_flag()
        self.testlist_manager.reset_switch_testfile_flag()
        return ret
    #注册WorkingInfoManager obj
    def gen_WorkingInfo_manager_instance(self,cfg):
        self.db_path = self.spacePath+"/workingInfo.db"
        self.workingInfoObj = WorkingInfoManager(persistentDBName=self.db_path)
        self._boot_workspace_workingInfo(cfg)
        return self.workingInfoObj
    def gen_WorkingInfo_manager_instance_with_json(self,jsonfile,json_rd_only=0):
        self.db_path = self.spacePath+"/workingInfo.db"
        self.workingInfoObj = WorkingInfoManager(persistentDBName=self.db_path)
        jsonfile = self.spacePath+"/"+jsonfile
        self._boot_workspace_workingInfo_with_json(jsonfile,rd_only=json_rd_only)
        return self.workingInfoObj
    def get_workingInfo_manager_instance(self):
        return self.workingInfoObj

    #通过workingInfo obj获取当前的working信息，就是cfg中配置的mark等信息
    def _boot_workspace_workingInfo(self,cfg):
        self.workingInfoObj.boot_WorkingInfo_wirh_cfg(cfg)
        self.workingInfoObj.boot_workingInfo_counter()#boot WorkingInfo持久化数据库
        self.types_arr = self.workingInfoObj.mark
        self._workingInfo = self.workingInfoObj.get_counter_arr()

    def _boot_workspace_workingInfo_with_json(self,jsonfile,rd_only=0):
        #rd_only = 0时仅仅用于打印目前环境可用的id
        self.workingInfoObj.boot_WorkingInfo_with_json(jsonfile,rd_only=rd_only)
        self.workingInfoObj.boot_workingInfo_counter()#boot WorkingInfo持久化数据库
        self.types_arr = self.workingInfoObj.mark
        self._workingInfo = self.workingInfoObj.get_counter_arr()

    #boot workspace是依赖于workingInfoObj的注册
    def boot_workspace(self):
        if self.workingInfoObj != NotImplemented:
            if os.path.exists(self.note_path):
                curr = open(self.note_path,"r")
                curr_info = curr.readline()
                curr.close()
                info = self.get_cmdline(curr_info)
                self.desc = str(info[0])
                #self.db_path = str(info[1])   ##db path在中途不能修改，该变量只在boot counter的时候被赋值一次
                self.reset_wi_counter=str(info[2])
                self._workingInfo = self.workingInfoObj.get_counter_arr()
            else:
                self.update_cmdline_note()
        else:
            print "[Error]boot workspace wrong,please reboot it later..."
    

    def get_spaceName(self):
        return self.spaceName
    def get_spacePath(self):
        return self.spacePath
    def get_priv_testlist_path(self):
        return self.priv_testlist_path
    def get_note_path(self):
        return self.note_path
    def get_types_arr(self):
        return self.types_arr
    def get_desc(self):
        return self.desc


    def get_work_info_counter(self):
        return self._workingInfo

    #通过open_workspace的参数src_suffix，选择哪个文件为当前运行的default文件
    def __src_switch_by_suffix(self,src_suffix):
        print src_suffix
        if src_suffix is None:
            src_testlist_path = self.cwd+"/./src/default/testlist.txt"
            src_default_cfg_path = self.cwd+"/./src/default/default.cfg"
        else:
            src_testlist_path = self.cwd+"/./src/"+str(src_suffix)+"/testlist.txt"
            src_default_cfg_path = self.cwd+"/./src/"+str(src_suffix)+"/default.cfg"
        src_path = {
            "testlist":src_testlist_path,
            "default_cfg":src_default_cfg_path
        }
        print "[SRC COPY FROM]",src_path
        return src_path
    def open_workspace(self,src_suffix=None):
        #step1:mkdir workspace
        _spacePath = self.spacePath
        #print _spacePath
        if not os.path.exists(_spacePath):
            #print "no dir",_spacePath
            os.mkdir(_spacePath)
        #step2:prepare workspace env.
        #    1)testlist:copy from ./src/testlist.txt
        _priv_testlist_path = self.priv_testlist_path
        src_path_dict = self.__src_switch_by_suffix(src_suffix)
        src_testlist_path = src_path_dict["testlist"]
        src_default_cfg_path = src_path_dict["default_cfg"]
        if not os.path.exists(_priv_testlist_path):
            testlist = open(src_testlist_path,"r")
            testlines = testlist.read()
            testlist.close()
            testlist_priv = open(_spacePath+"/testlist_priv.txt","w")
            testlist_priv.write(testlines)
            testlist_priv.close()
        else:
            testlist_priv = open(_spacePath+"/testlist_priv.txt","r")
            co = testlist_priv.read()
            testlist_priv.close()
            if re.sub(r"\s{1,}","",co) == "":
                testlist = open(src_testlist_path,"r")
                testlines = testlist.read()
                testlist.close()
                testlist_priv = open(_spacePath+"/testlist_priv.txt","w")
                testlist_priv.write(testlines)
                testlist_priv.close()
        """
        if not os.path.exists("fpga_debug.log"):
            log = open("fpga_debug.log","a+")
        else:
            log = open("fpga_debug.log","w")
        log.write("curr space:"+spaceName+"\n")
        
        log = open(self.cwd+"/../"+str(self.platform)+"_debug.log","w")
        log.write(_spacePath)
        log.close()
        """
        if not os.path.exists(self.spacePath+"/priv_default.cfg"):
            copyfile(src_default_cfg_path,self.spacePath+"/priv_default.cfg")
        #self.boot_workspace()
    #每次更新了当前的counter后必须存储到文件或者数据库中，因为自动化中每次都需要重新加载该脚本，需要每次都用上次的counter重新boot环境
    def update_cmdline_note(self):
        _python_ = "python"
        workspacePath  = self.spacePath
        _note_path = self.note_path
        if not os.path.exists(_note_path):
            #print "no dir", _note_path
            curr = open(_note_path, "w")
            curr.close()
            self.update_cmdline_note()
        else:
            bash_name = "run.py"
            curr = open(_note_path,"w")
            content = _python_+" "+bash_name +" "
            content += "-desc "+str(self.desc)+ " "
            content += "-workingInfoCounterDB "+str(self.db_path)+" "
            content += "-resetCounterFlag "+str(self.reset_wi_counter)+" "
            #content += "-change_testlist_flag "+str(self.change_testlist_flag)+" "
            print "\n\n\n============================>>>update_curr start<<<====================================="
            print "update_curr_note >>> " + content
            print "============================>>>update_curr end<<<======================================="
            curr.write(content)
            curr.close()


    def update_curr_cmdline_wrap(self,step_add):
        _desc = self.desc
        note_path = self.note_path
        if not os.path.exists(note_path):
            #print "no dir", note_path
            curr = open(note_path, "w")
            curr.close()
            self.update_cmdline_note()
        else:
            curr = open(note_path,"r")
            co = curr.read()
            curr.close()
            if re.sub(r"\s{1,}","",co) == "":
                self.update_cmdline_note()
            else:
                curr = open(note_path,"r")
                curr_info = curr.readline()
                curr.close()
                value = self.get_cmdline(curr_info)
                self.desc = str(value[0])
                #self.db_path = str(value[1])   ##db path在中途不能修改，该变量只在boot counter的时候被赋值一次
                self.reset_wi_counter=int(value[2])
                #self.change_testlist_flag=int(value[3])
                self._workingInfo = self.workingInfoObj.update_workingInfo_counter(step_add)
                if self.workingInfoObj.get_finish_flag():
                    self.reset_wi_counter = 1
                    print "[OBJ DOWN]  >>>  finish_current_testfile"
                    self.testlist_manager.finish_current_testfile()
                    
                self.try_reset_workingInfo_counter()
                self.update_cmdline_note()
    #当reset_wi_counter flag为1时，则做reset操作，否则不做
    def try_reset_workingInfo_counter(self):
        ret = 0
        if self.reset_wi_counter:
            self._workingInfo = self.workingInfoObj.update_workingInfo_counter(0)
            ret = 1
        self.reset_wi_counter = 0
        return ret


    @staticmethod
    def get_cmdline(cmd):
        words = cmd.split(" ")
        #print words
        info = []
        for i in range(0,len(words)):
            if re.match(r"-",words[i]) !=None:
                info.append(words[i+1])
        #print "new note >>> ",info
        return info

    def mkdir_in_workspace(self,dirname):
        path = ''.join ( (self.spacePath, '/',dirname) )
        if not os.path.exists(path):
            #print "no dir ",path
            os.mkdir(path)
        return path

    def open_env_with_cfg(self,cfg):
        self.open_workspace()
        self.gen_testlist_manager_instance().boot_testlist_env_status()
        self.gen_WorkingInfo_manager_instance(cfg)
        self.boot_workspace()
        return self

class working_log():
    def __init__(self,log_file_name,log_dir):
        self.log_dir = log_dir
        if log_file_name == "":
            self.log_file_name = "workspace_working.log"
        self.log_path = self.log_dir+"/"+self.log_file_name
        self.log = self.new_log_file()
        self.log_keys = []

    def new_log_file(self):
        log = open(self.log_path,"w")
        return log

    def open_log_file(self):
        log = open(self.log_path,"a+")
        self.log = log

    def save_log_file(self):
        log = self.log.close()

    def write_log(self,key,value):
        self.open_log_file()
        self.log.write(key+":"+value+"\n")
        self.log_keys.append(key)
        self.save_log_file()

    def get_value(self,key):
        self.open_log_file()
        lines = self.log.readlines()
        value = ""
        for line in lines:
            re_in = str(key)+":"
            re_ret = re.match(re_in,line)
            if (re_ret)!=None:
                value = line.strip("\n").split(":")[1]
        if value=="":
            print "[Error]working_log >>> get_value::key is wrong... "
        return value


