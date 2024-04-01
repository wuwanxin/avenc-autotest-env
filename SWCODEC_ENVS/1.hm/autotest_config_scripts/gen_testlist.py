
#-*-coding:utf-8*-
import os
import sys
import glob
import re
import time
import datetime
import cfg


cwd_path = os.path.abspath(sys.argv[0])
cwd = os.path.dirname(cwd_path)
#print cwd
sys.path.append(cwd+"/../depending_scripts")
#print dir()
#print __package__
#from depending_scripts import *
import cmdline_parser_new
import work_env_utils
import worksapce_tools




codec = ["hevc","avc",'jpeg']
c_model_dir = "../c_model/"
cmdline_title_arr = ["hevc_testenc_vc8000e","h264_testenc_vc8000e","jpeg_testenc_vc8000e"]
Persize = 0x9000000


parse_utils = cmdline_parser_new.parse_utils(type=0)
change_line = parse_utils.change_line_func
parse_cmdline = parse_utils.parse_cmdline_func
get_line_value = parse_utils.get_line_value_func






def gen_case_info_dict(my_curr_info,test_case_dict):

    #yuv basic info 
    org_yuv_path = test_case_dict["org"]
    yuv_name = os.path.basename(org_yuv_path)

    strs = yuv_name.split('_')
    picxy = strs[1].split('x')
    framerate = strs[2].split('fps')[0]
    framenum = strs[3].split('f')[0]
    framenum = int(framenum)

    

    real_yuv_path = test_case_dict["after_filter"]
    yuv_dir = os.path.dirname(real_yuv_path)
    
    case_info_dict = {
        "src_dir":yuv_dir,
        "src_name":yuv_name,
        "src_path":real_yuv_path,
        "width":picxy[0],
        "height":picxy[1],
        "framerate":framerate,
        "framenum":framenum,
        "base_dir":my_curr_info.get_cur_envs_of_group_path()
    }

    others = test_case_dict["others"]
    for key,values in others.items():
        case_info_dict[key] = values
    print case_info_dict
    return case_info_dict


#====================修改生成tag.cfg=================
#除了input 和 output之外的所有要生效的参数配置需要在此处进行修改
def changeYuvFileInfo(cfg_line,src_type,case_info_dict,_codec,out_change_flag):
    str = ''
    """
    yuvname = input_path.split("/")[-1]
    strs = yuvname.split('_')
    picxy = strs[1].split('x')
    framerate = strs[2].split('fps')[0]
    framenum = strs[3].split('f')[0]
    framenum = int(framenum)-2
    """
    yuvname = case_info_dict["src_name"]
    yuvpath = case_info_dict["src_path"]
    picx = int(case_info_dict["width"])
    picy = int(case_info_dict["height"])
    framerate = int(case_info_dict["framerate"])
    framenum = int(case_info_dict["framenum"])
    # if "dec400" in src_type:
    #     ret = change_line(cfg_line, (picx+128-1)>>7<<7,"--lumWidthSrc")
    # else:
    #     ret = change_line(cfg_line, picx,"--lumWidthSrc")
    ret = change_line(cfg_line, picx,"--SourceWidth")
    ret = change_line(ret, picy,"--SourceHeight")
    ret = change_line(ret, framerate,"--FrameRate")
    ret = change_line(ret, framenum,"--FramesToBeEncoded")
    
    
    return ret

def register_funcs(parser,workInfoManager=None,my_curr_info=None,case_info_dict=None,bs_path=None,codec=None):
    #1
    @parser.register_func_changeCfgLine
    def changeCfgline():
        line = getattr(parser, "line")
        wim = workInfoManager
        return wim.change_df_cfg(line,parse_utils)

    #2.changeStreamInfo函数不带参数，所以需要的参数通过setattr添加进去，再在changeStreamInfo（）中通过getattr获取
    @parser.register_func_changeStreamInfo
    def changeStreamInfo():
        out_change_flag = 1
        line = getattr(parser,"line")
        return changeYuvFileInfo(line,my_curr_info.get_curr_env_src_type(),case_info_dict,codec,out_change_flag)
#===========================================================


#====================修改生成id.cfg=================
def changeYuvIDInfo(line, case_info_dict, id_ignore):
    ret = line
    #忽略掉的配置项
    for ig in id_ignore:
        ret = change_line(ret, "#", ig)

    yuvpath = case_info_dict["src_path"]
    ret = change_line(ret, yuvpath, "--InputFile")
    

    return ret

#这个方法中注册的是不影响其码流内容的值
def register_id_func(parser,case_info_dict=None,id_ignore=None):
    @parser.register_func_changeStreamInfo
    def changeStreamInfo():
        out_change_flag = 1
        line = getattr(parser,"line")
        return changeYuvIDInfo(line,case_info_dict,id_ignore)


#================修改input和output========
#====================修改生成最终的cfg=================
def changeYuvIOInfo(line, case_info_dict, output_path):
    ret = line
    #print "output_path",output_path

    name = os.path.basename(output_path)
    dir = os.path.dirname(output_path)
    #print "name",name
    #print "dir",dir
    base_dir = case_info_dict["base_dir"]
    yuvpath = case_info_dict["src_path"]
    if "nv12" in yuvpath:
        name = "nv12_" + name
    elif "yv12" in yuvpath:
        name = "yv12_" + name
    output_path = dir + "/" + name
    ret = change_line(ret, yuvpath, "--InputFile")
    ret = change_line(ret, output_path, "--BitstreamFile")

    value = get_line_value(ret, "--roiMapDeltaQpFile")
    if value:
        ret = change_line(ret, base_dir+"/"+value, "--roiMapDeltaQpFile")
    
    value = get_line_value(ret, "--ipcmMapFile")
    if value:
        ret = change_line(ret, base_dir+"/"+value, "--ipcmMapFile")
    
    value = get_line_value(ret, "--userData")
    if value:
        ret = change_line(ret, base_dir+"/"+value, "--userData")
    
    #jpeg
    # value = get_line_value(ret, "--inputThumb")
    # if value:
    #     ret = change_line(ret, base_dir+"/"+value, "--inputThumb")
    return ret
def register_io_func(parser,case_info_dict=None,bs_path=None):
    @parser.register_func_changeStreamInfo
    def changeStreamInfo():
        out_change_flag = 1
        line = getattr(parser,"line")
        return changeYuvIOInfo(line,case_info_dict,bs_path)


#===================filter======================
#kwargs默认有testcase
#自定义部分:
#   1)自定义的参数在FilterFunc中添加
#   2）自定义的参数在FilterFuncKwargs返回值中添加
def FilterFuncKwargs(my_curr_info):
    return {
        "platform":my_curr_info.get_platform(),
        "src_type":my_curr_info.get_curr_env_src_type()
    }

#org是testlist.txt中实际的配置内容，其内容才是真正参与到后期的cfg生成中
#org可以不是实际存在的，真正的地址由filter中生成
#该特性可以由用户自定义，下方注释diy start的位置开始为自定义配置起始处，主要配置after_filter和others
# key ::　after_filter  表示 经过filter之后的内容，一般为地址，如果是地址必须是实际地址（若不是地址需要改drv）
# key ::  others  表示 除了通过testlist中的内容以外的其他携带的东西，一般是地址（若不是地址需要改drv）
#    （目前的drv只支持地址，且　after_filter和others配置的地址会一起使用）
def FilterFunc(testcase,platform=None,src_type=None):
    #testcase = cwd + "/" + testcase
    #print  testcase
    #print platform
    #others必须是字典,其中的key可以在配置cfg中使用
    testcase_name = os.path.basename(testcase)
    testcase_dir = os.path.dirname(testcase)
    #print  testcase_name
    #print  testcase_dir
    ret = {
        "org":"",
        "after_filter":"",
        "others":{}
    }

    ret["org"] = testcase
    ret["after_filter"] = ret["org"]
    print "testcase :: ",testcase
# diy start
    if not src_type:
        return ret
    if "dec400" in src_type:
        if platform=="FPGA":
            ret["after_filter"] = testcase_dir + "/dec400/" + testcase_name.split(".")[0]+"_dec400.yuv"
            other = ret["others"]
            other["dec400"] = testcase_dir + "/dec400/" + testcase_name.split(".")[0]+"_dec400.tab"

        elif platform=="REF_C":
            ret["after_filter"] =  testcase_dir + "/align128/" + testcase_name.split(".")[0]+"_align128.yuv"

    return ret


