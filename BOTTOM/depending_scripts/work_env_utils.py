#!/usr/bin/env python 
#-*-coding:utf-8*-
import re
import os



class WorkingInfoManager:
    mark = []
    mark_param = []
    marklen = []
    change_cmdline_group = []
    def __init__(self,persistentDBName="workingInfo.db"):
        self.persistentDBName = persistentDBName
        self.turn_finished = 0
    def attrs(self,**kwds):
        for k in kwds:
            setattr(self,k,kwds[k])

    def update_db(self,workingInfoConters):
        if self.turn_finished:
            self.mark_type_id = 0
            self.turn_id = 0
            self.work_times = 0
            workingInfoConters = []
            workingInfoConters = [0,0,0]
            self.finish_flag = 0
        db = open(self.persistentDBName,"w")
        content = "mark_type:"+str(self.mark[workingInfoConters[0]])+"\n"
        content += "mark_type_id:"+str(workingInfoConters[0])+"\n"
        content += "turn_id:"+str(workingInfoConters[1])+"\n"
        content += "work_times:"+str(workingInfoConters[2])
        #print content
        db.write(content)
        db.close()

    def boot_workingInfo_counter(self):
        self.get_workingInfo_counter_from_db()

    def get_mark_type_turn_param(self):
        return self.mark_param[int(self.mark_type_id)][int(self.turn_id)]
    def get_mark_type(self):
        return self.mark[int(self.mark_type_id)]
    def get_turn_id(self):
        return self.turn_id
    def get_work_times(self):
        return self.work_times
    def get_mark_type_id(self):
        return self.mark_type_id
    def set_finish_flag(self,flag):
        self.turn_finished = flag
    def get_finish_flag(self):
        return self.turn_finished
    def get_workingInfo_counter_from_db(self):
        mark_type_id = 0
        turn_id = 0
        work_times = 0
        if os.path.exists(self.persistentDBName):
            db = open(self.persistentDBName,"r")
            db_lines = db.readlines()
            db.close()
            if len(db_lines)!=0:
                for line in db_lines:
                    line = line.strip("\n")
                    re_in = "^"+"mark_type:"
                    if re.match(re_in,line) != None:
                        mark_type = str(re.sub(re_in,"",line))
                    re_in = "^"+"mark_type_id:"
                    if re.match(re_in,line) != None:
                        mark_type_id = int(re.sub(re_in,"",line))
                    re_in = "^"+"turn_id:"
                    if re.match(re_in,line) != None:
                        turn_id = int(re.sub(re_in,"",line))
                    re_in = "^"+"work_times:"
                    if re.match(re_in,line) != None:
                        work_times = int(re.sub(re_in,"",line))
        self.mark_type_id = mark_type_id
        self.turn_id = turn_id
        self.work_times = work_times
        print "mark_type_id::",self.mark_type_id
        print "turn_id::",self.turn_id
        print "work_times::",self.work_times

    
    def update_workingInfo_counter(self,step):
        turn_id_overflow = 0
        remain_step = 0
        times = 0
        #当step不为1时，可能会存在一个step直接跳过了某个mark_type,所以使用remind_step来保存当前mark_type下剩余未操作的step
        while (not times) or (remain_step):
            times += 1
            ret = self.update_value(self.turn_id,len(self.mark_param[self.mark_type_id]),step,remain_step)
            turn_id_overflow = int(ret["overflow"])
            remind_step = int(ret["remain_step"])
            self.turn_id = int(ret["value"])
            #当超过当前mark_type的turn时，需要进位，mark_type_id+1
            #mark_type只可能按照step为1的方式累加，并且不可能出现remind_step 》》 step=1，remind_step=0
            #print "turn_id_overflow",turn_id_overflow
            if turn_id_overflow:
                #print " >>>  turn_id_overflow"
                ret = self.update_value(self.mark_type_id,len(self.mark),1,0)
                mark_type_overflow = int(ret["overflow"])
                self.mark_type_id=int(ret["value"])
                #当mark_type检测到溢出，则表示本轮结束。整个计数环境需要reset
                if mark_type_overflow:
                    self.set_finish_flag(1)
                else:
                    self.set_finish_flag(0)
            else:
                self.set_finish_flag(0)
        self.work_times+=1
        self.update_db([self.mark_type_id, self.turn_id, self.work_times])
        return [self.mark_type_id,self.turn_id,self.work_times]
        
    def get_counter_arr(self):
        return [self.mark_type_id,self.turn_id,self.work_times]


    def boot_WorkingInfo_wirh_cfg(self,cfg):
        for k in getattr(cfg,"mark"):
            k = str(k)
            param = getattr(cfg,k)
            self.mark.append(k)
            self.mark_param.append(param)
            self.check_types_arr(self.mark_param)
            setattr(self,k,param)
            self.marklen.append(len(param))
            change_cmdline_rules = getattr(cfg,k+"_rules")
            self.change_cmdline_group.append(change_cmdline_rules)
            setattr(self,k+"_rules",change_cmdline_rules)

    def boot_WorkingInfo_with_json(self,jsonfile,rd_only=0):
        import json
        file = open(jsonfile, "rb")
        fileJson = json.load(file)
        file.close()
        id = 0
        for mark in fileJson:
            #print mark
            k = mark["mark_name"]
            #param = mark["mark_arr"]
            # "#"和"+"表示不测，具体含义可以用户自定义，目前该标识在其他地方都没用
            skip_flag = (re.match(r"^#",k) != None)
            ok_flag = (re.match(r"^[+]",k) != None)
            wrong_flag = (re.match(r"^[-]",k) != None)
            #print skip_flag
            #print ok_flag
            if (not skip_flag) and (not ok_flag) and (not wrong_flag):
                if rd_only:
                    print "[BOOT MARKS]id-",str(id)," ::",k
                    id+=1
                else:
                    print "[BOOT MARKS]id-",str(id)," ::",k
                    id+=1
                    change_cmdline_rules_dic = mark["mark_rules"]
                    change_cmdline_rules = []
                    param_arr = []
                    for key in change_cmdline_rules_dic.keys():
                        value = change_cmdline_rules_dic[key]
                        change_cmdline_rules.append([key,value])
                        #判断param的类型,一组mark中只能有一个param是list
                        if isinstance(value,list):
                            param_arr = value
                    self.mark.append(k)
                    self.mark_param.append(param_arr)
                    self.check_types_arr(self.mark_param)
                    setattr(self, k, param_arr)
                    self.marklen.append(len(param_arr))
                    setattr(self, k + "_rules", change_cmdline_rules)
            else:
                print "[BOOT MARKS]",k," do not process..."


    #把空的转换成"NA"
    def check_types_arr(self,types_arr):
        arr_arr = types_arr
        for i in range(0,len(arr_arr)):
            if len(arr_arr[i])==0:
                arr_arr[i].append("NA")

    def __find_change_times(self,mark_type):
        times = len(getattr(self,mark_type))
        return times
            
    def change_df_cfg(self,line,parser):
        ret = line
        change_cmdline_rules = getattr(self,str(self.get_mark_type())+"_rules")
        for j in range(0,len(change_cmdline_rules)):
            tmp = change_cmdline_rules[j]
            if isinstance(tmp[1],list):
                if isinstance(tmp[1][self.turn_id],list):
                    p_key = tmp[0]
                    p_value = tmp[1][self.turn_id]
                    for id in range(0,len(p_key)):
                        ret = parser.change_line_func(ret, str(p_value[id]), p_key[id])
                else:
                    ret = parser.change_line_func(ret, str(tmp[1][self.turn_id]), tmp[0])
            else:
                ret = parser.change_line_func(ret,str(tmp[1]), tmp[0])
        return ret
    
    @staticmethod
    def update_value(value,overflow_len,add_step,remain_step):
        limit = overflow_len - 1
        add_limit = limit-value
        overflow = 0 
        add_step += remain_step
        if(add_step<=add_limit):
            remain_step = 0
            value_new = value+add_step
            value = value_new%overflow_len
            #print "db workinginfo counters :: if overflow >>> value:",value," overflow_len",overflow_len
            if(value_new>value):
                overflow = 1
                #print "sh workinginfo :: overflow"
        else:
            remain_step = add_step-add_limit
            value = 0
            overflow = 1
            #print "sh workinginfo :: overflow"
        if add_step:
            #print "value ",value,"  |||   overflow ",overflow,"      |||   remain_step ",remain_step
            pass
        ret = {"value":value,"overflow":overflow,"remain_step":remain_step}
        return ret