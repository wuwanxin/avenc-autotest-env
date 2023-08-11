#-*-coding:utf-8*-
import re,os

class testlistManager:
    def __init__(self,testlist_path,testfile_limit_size=None):
        self.priv_testlist_path = testlist_path
        self.size_limit = testfile_limit_size
        self.end_flag = 0
        self.switch_testfile_flag = 0
        self.current_testfile = None
        #self.status = self.boot_testlist_env_status()
        self.status = None
        self.filter = None
        #working glob param
        self.__through_lines = None


    def set_change_testlist_flag(self,flag):
        self.change_testfile_flag = flag
    def get_change_testfile_flag(self):
        return self.change_testfile_flag
    def set_end_flag(self,flag):
        self.end_flag = flag
    def get_end_flag(self):
        return self.end_flag
    def get_switch_testfile_flag(self):
        return self.switch_testfile_flag
    def reset_switch_testfile_flag(self):
        self.switch_testfile_flag = 0


    def set_filter(self,target=NotImplemented,args=None,kwargs=None):
        self.filter = testlistFileter(self, target=target,args=args, kwargs=kwargs)

    def get_current_testfile(self):
        if self.filter:
            return self.filter.doFilter()
        ret = {
             "org":self.current_testfile,
             "after_filter":self.current_testfile,
             "others":{}
         }
        return ret

    def get_current_testfile_no_filter(self):
        return self.current_testfile
    def __sign_testfile(self,yuv_name,sign):
        #flag = 0 :: size error >> ### >> __sign_error_testfile
        #flag = 1 :: working    >>  #
        #flag = 2 :: down       >>  ##
        fp = open(self.priv_testlist_path,"r")
        yuvlines = fp.readlines()
        fp.close()
        fp = open(self.priv_testlist_path,"w")
        for fp_line in yuvlines:
            if yuv_name in fp_line:
                fp.write(sign + fp_line)
            else:
                fp.write(fp_line)
        fp.close()

    def __sign_error_testfile(self,yuv_name,error_sign):
        #flag = 0 :: size error >> ###
        #flag = 1 :: working    >>  #
        #flag = 2 :: down       >>  ##
        fp = open(self.priv_testlist_path,"r")
        yuvlines = fp.readlines()
        fp.close()
        fp = open(self.priv_testlist_path,"w")
        for fp_line in yuvlines:
            if re.match(r'^#{1,}[^#]', fp_line, re.M) == None:
                if yuv_name in fp_line:
                    fp.write(error_sign + fp_line)
                else:
                    fp.write(fp_line)
            else:
                fp.write(fp_line)
        fp.close()


    def __end_current_file(self):
        if self.get_end_flag():
            #print "[END]testlist end..."
            return
        status = self.status
        flags = status[0]
        #print "   >>>>   __end_current_file >>> flags",flags
        testfiles = status[1]
        #print "   >>>>   __end_current_file >>> testfiles",testfiles
        next_testfile = testfiles[1]
        if flags[0]:
            self.__sign_testfile(testfiles[0],"#")
            #print "testlist_manager::__end_testlist  =>>   sign end testfilename",testfiles[0]
        if not flags[1]:
            self.set_end_flag(1)
        self.__update_testlist_env_status()
    def __excute_testlist(self):
        if self.get_end_flag():
            #print "yuvlist end..."
            return
        status = self.status
        flags = status[0]
        testfiles = status[1]
        next_testfile = testfiles[1]
        if flags[1]:
            self.__sign_testfile(testfiles[1],"#")
            #print "testlist_manager::__excute_testlist  =>>   sign start testfilename",testfiles[1]
        self.__update_testlist_env_status()
        self.__check_current_status()

    def __size_check(self,file_path):
        sign = None
        org = file_path

        if self.filter:
            file_path_name = re.sub(r'^#{1,}', "", file_path).rstrip()
            case = self.filter.get_case_through_filter(file_path_name)
        else:
            file_path_name = re.sub(r'^#{1,}', "", org).rstrip()
            case = file_path_name
        if self.size_limit != None:
            print os.getcwd()
            fileSize = os.path.getsize(case)
            if fileSize > self.size_limit:
                self.__sign_error_testfile(org,"###")
                print "[Error]oversize.."
                return 0
            else:
                return 1

        else:
            return 1

    #找到last（正在执行的file），next（下一次执行的file）
    def __update_testlist_env_status(self):
        last_yuv = ""
        find_last = 0
        find_next = 0
        next_yuv = ""
        yuvlines = self.__get_testlist_lines()
        #print yuvlines
        for line in yuvlines:
            if find_last and find_next:
                break
            yuv_name = re.sub(r'^#{1,}',"",line).rstrip()
            if((find_last==0) and (re.match(r'^#{1}[^#]', line, re.M)) != None):#   "like #yuvname"
                last_yuv =  yuv_name
                find_last = 1
                #print "testfile_manager find woking testfile ... ",yuv_name
                continue
            if((find_next==0) and(re.match(r'^#', line, re.M)) == None) :  #   "like   yuvname"
                next_yuv = yuv_name
                find_next = 1
                #print "testfile_manager find next change yuv ... ",yuv_name
        flag = []
        flag.append(find_last)
        flag.append(find_next)
        testfile = []
        testfile.append(last_yuv)
        testfile.append(next_yuv)
        _status = []
        _status.append(flag)
        _status.append(testfile)
        self.status =_status
        return _status
    def boot_testlist_env_status(self):
        _status = self.__update_testlist_env_status()
        self.__check_current_status()
        return self.status
    def reboot_testlist_env_status(self):
        _status = self.__update_testlist_env_status()
        self.__check_current_status()
        self.status = _status

    def __check_current_status(self):
        flags = self.status[0]
        files = self.status[1]
        find_last = flags[0]
        find_next = flags[1]
        if (not find_last)and(not find_next):
            self.set_end_flag(1)
        if find_last :
            self.current_testfile = files[0]
        if (not find_last) and find_next:
            #切换
            self.switch_testfile_flag = 1
            self.__excute_testlist()
            return
        #print ">>>func>>>testlistManager::__check_current_status() =>  current_testfile ",self.current_testfile
        #print ">>>func>>>testlistManager::__check_current_status() =>  param find_last ",find_last
        #print ">>>func>>>testlistManager::__check_current_status() =>  param find_next ",find_next
        print "[WORKING OBJ] => ",self.current_testfile
        print "\n\n\n"



    def __get_testlist_lines(self):
        #print self.priv_testlist_path

        fp = open(self.priv_testlist_path,"r")
        lines = fp.readlines()
        fp.close()
        __through_lines = []
        for line in lines:
            if line.strip(" ").rstrip() == "":
                continue
            line = line.rstrip()
            print "line::",line
            if re.match(r'^#{2,}[^#]', line, re.M) == None:
                if self.__size_check(line):
                    __through_lines.append(line)
        self.__through_lines = __through_lines
        return self.__through_lines

    def finish_current_testfile(self):
        yuv = self.__end_current_file()


    # ret = {
    #     "org":"",
    #     "after_filter":"",
    #     "others":{}
    # }
    # doFilter返回的结构
class testlistFileter:
    def __init__(self,testManager,target=NotImplemented,args=None,kwargs=None):
        if kwargs is None:
            kwargs = {}
        self.__obj = testManager
        self.__target = target
        self.__kwargs = kwargs
        self.__args = args
        self.bypass = False
        if target is NotImplemented:
            self.bypass = True

    #filter的作用是把 a 映射为 b
    # a>>testlist中的内容
    # b>>根据自己的需求转换后的结果
    #filer完全是用户配置的，若不配置，其结果就是原始testlist中的内容
    def doFilter(self):
        testcase = self.__obj.get_current_testfile_no_filter()
        return self.__testcaseDoFilter(testcase)

    def __testcaseDoFilter(self,testcase):
        try:
            if self.bypass:
                return testcase
            else:
                if self.__target:
                    self.__kwargs["testcase"] = testcase
                    print self.__kwargs
                    return self.__target(**self.__kwargs)
                else:
                    print "[error]...__target should be implemented.."
        finally:
            pass
            #del self.__target, self.__kwargs

    #经过a经过filter后转换为a1
    #并且还可能携带了一些其他文件
    #该函数返回a1
    def get_case_through_filter(self,testcase):
        return self.__testcaseDoFilter(testcase)["after_filter"]