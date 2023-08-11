#-*-coding:utf-8*-
import os
import sys
import glob
import re
import datetime
from work_env_utils import WorkingInfoManager
class parse_utils:
    change_line_func = NotImplemented
    parse_cmdline_func = NotImplemented
    get_line_value_func = NotImplemented
    def __init__(self,type):
        if type == 0:
            self.change_line_func = self.change_line
            self.get_line_value_func = self.get_line_value
        elif type == 1:
            self.change_line_func = self.change_line_rule2
        self.parse_cmdline_func = self.parse_cmdline
    # -low_key :: --long_key :: value
    @staticmethod
    def parse_cmdline(cfg_line):
        cmd = ""
        if re.match(r"\s{0,}[^#]+::",cfg_line) !=None:
            cfg_line = str(cfg_line)
            cfg = cfg_line.split("::")
            short_key = cfg[0].strip(" ").strip("\n")
            long_key = cfg[1].strip(" ").strip("\n")
            value = cfg[2].strip(" ").strip("\n")
            if(re.search(r'NULL',cfg[0]) != None):
                key = " "+long_key
            else:
                key = " "+short_key
            cmd = str(key) + " " + str(value)
            #print cmd
        return cmd

    


    """
    type : commend line name,to match the cmd line . 

    value = "#"   : change line to comment .
    value != "#"  : set value to the matched cmd line .

    """
    @staticmethod
    def change_line1(org_line,value,type):
        new_line = None
        #匹配，0个或多个空格，加上非#号的符号，贪婪模式匹配到：：号
        re_ret = re.match(r"\s{0,}[^#]+::",org_line)
        if re_ret!=None:
            #print re_ret.group()
            re_in = str(type)+"\s"        
            if(re.search(re_in,re_ret.group())):
                if str(value) != "#":
                    new_line = re_ret.group() + str(value) + "\n"
                else:
                    new_line = "#" + str(org_line)
        if new_line==None:
            new_line = org_line
        else:
            print "==================change_line===========>>>  " + new_line
        return new_line

    @staticmethod
    def change_line(org_line, value, type):
        new_line = None
        if re.match(r"^#",type):
            re_ret = re.match(r"\s{0,}#{0,}.+::", org_line)
            if re_ret != None:
                type=type.strip("#")
                re_in = str(type) + "\s"
                line = re_ret.group().strip("#")
                if (re.search(re_in, line)):
                    if str(value) != "#":
                        new_line = line + str(value) + "\n"
                    else:
                        new_line = "#" + str(org_line)
        else:
            re_ret = re.match(r"\s{0,}[^#].+::", org_line)
            if re_ret != None:
                # print re_ret.group()
                re_in = str(type) + "\s"
                if (re.search(re_in, re_ret.group())):
                    if str(value) != "#":
                        new_line = re_ret.group() + str(value) + "\n"
                    else:
                        new_line = "#" + str(org_line)
        if new_line == None:
            new_line = org_line
        else:
            print "==================change_line===========>>>  " + new_line
        return new_line

    @staticmethod
    def get_line_value(org_line, type):
        value = None
        if re.match(r"^#", type):
            re_ret = re.match(r"(\s{0,}#{0,}.+::)(.+.)", org_line)
            if re_ret != None:
                type = type.strip("#")
                re_in = str(type) + "\s"
                line = re_ret.group(1).strip("#")

                if (re.search(re_in, line)):
                    key = type
                    value = re_ret.group(2).rstrip().strip(" ")
        else:
            re_ret = re.match(r"(\s{0,}[^#].+::)(.+.)", org_line)
            if re_ret != None:
                # print re_ret.group()
                re_in = str(type) + "\s"
                if (re.search(re_in, re_ret.group(1))):
                    key = type
                    value = re_ret.group(2).rstrip().strip(" ")

        return value
    @staticmethod
    def load_line(org_line, type):
        value = None
        if re.match(r"^#", type):
            re_ret = re.match(r"(\s{0,}#{0,}.+::)(.+.)", org_line)
            if re_ret != None:
                type = type.strip("#")
                re_in = str(type) + "\s"
                line = re_ret.group(1).strip("#")

                if (re.search(re_in, line)):
                    key = type
                    value = re_ret.group(2).rstrip().strip(" ")
        else:
            re_ret = re.match(r"(\s{0,}[^#].+::)(.+.)", org_line)
            if re_ret != None:
                # print re_ret.group()
                re_in = str(type) + "\s"
                if (re.search(re_in, re_ret.group(1))):
                    key = type
                    value = re_ret.group(2).rstrip().strip(" ")

        return value
    # key = value 
    @staticmethod
    def change_line_rule2(org_line,value,type):
        #print "change_line2"
        comment = ""
        new_line = None
        ret = re.match(r"(\s{0,}[^#]+=)(.*?).([#]{1,}.*)",org_line)
        if ret != None:
            #print "match ,this line has comment..."
            key = str(ret.group(1))
            old_value = str(ret.group(2))
            comment = str(ret.group(3))
        else:
            ret =  re.match(r"(\s{0,}[^#]+=)(.*)",org_line)
            if ret != None:
                #print "match ,this line has no comment..."
                key = str(ret.group(1))
                old_value = str(ret.group(2))
            # else:
            #     print "not match ..."
        if ret != None:
            #print "match ...."
            re_in = str(type)        
            if(re.search(re_in,key)):
                new_line = key+' '+str(value)+' '+comment + "\n"
                #print "change ",str(old_value)," to ",str(value)
        if new_line==None:
            new_line = org_line
        else:
            print "==change_line==>>>  " + new_line
        return new_line
class cfg_processer:
    def __init__(self):
        self.changeStreamInfo = []#该方法是一个数组，可以注册多个方法,且后写的会覆盖之前写的
        self.change_df_cfg = NotImplemented

    def gen_new_cfg(self,org_cfg_path,new_cfg_path):
        if((len(self.changeStreamInfo) != 0)):
            print "func changeStreamInfo() has Implemented"
        if((self.change_df_cfg != NotImplemented)):
            print "func change_df_cfg() has Implemented"
        d_f = open ( org_cfg_path, "r" )
        d_f_content = d_f.readlines()
        d_f.close ()  # put the default_cfg content to the finall cfg
        cfgFile = open(new_cfg_path, "w")
        for cfg_line in d_f_content:
            #print "======================>>cfg_line<<=============  !!! >>>>  " + cfg_line
            new_line = cfg_line
            setattr(self,"line",new_line)
            for func in self.changeStreamInfo:
                new_line = func()
            setattr(self, "line", new_line)
            if self.change_df_cfg != NotImplemented:
                new_line = self.change_df_cfg()
            cfgFile.write(new_line)
            #print "======================>>new_line<<=============  !!! >>>>  " + new_line
        cfgFile.close()

    #目前要转成命令行格式的只支持 a :: b :: c 格式的cfg
    def parse_cfg2args(self,cfg_path,cmdline_title,output_args_path=""):
        cfg = open(cfg_path,"r")
        cfg_lines = cfg.readlines()
        cfg.close()
        cmdline_agrs = ""
        for line in cfg_lines:
            line = line.strip("\n").strip("\r")
            cmdline_agrs = cmdline_agrs + parse_utils.parse_cmdline(line).strip("\n").strip("\r")
        print "\n\n\n======================>>cmdline<<========================="
        #2020-06-10：添加换行符，该符号与解析函数是对应起来的
        cmdline = "".join((cmdline_title, cmdline_agrs))+"\n"
        print cmdline
        print "======================>>cmdline<<========================="
        if output_args_path != "":
            args = open(output_args_path,"w")
            args.write(cmdline)
            args.close()
        return cmdline

    def load_cfg(self,cfg_path,paser_tool,types=[]):
        cfg = open(cfg_path, "r")
        cfg_lines = cfg.readlines()
        cfg.close()
        cfg_sets = {}
        if types is None:
            types = []
        for t in types:
            for line in cfg_lines:
                line = line.strip("\n").strip("\r")
                v = paser_tool.load_line(line,t)
                cfg_sets[t] = v


    def register_func_changeCfgLine(self,func):
        self.change_df_cfg = func


    def register_func_changeStreamInfo(self,func):
        self.changeStreamInfo.append(func)


    def attrs(self,**kwds):
        for k in kwds:
            #print k," ",kwds[k]
            setattr(self,k,kwds[k])