#-*-coding:utf-8*-
import os
import sys
import time
import re
import datetime
import shutil
from Queue import Queue
from multiprocessing import Process
import threading

cwd_path = os.path.abspath(sys.argv[0])
cwd = os.path.dirname(cwd_path)


os.chdir(cwd)
cwd = re.sub(r"\\{1,}","/",cwd,0)
platform = "PC_X86_64"

len_argv = len(sys.argv)-1
if len_argv>0:
    run_bash = int(sys.argv[1])
    process_total = int(sys.argv[2])
else:
    run_bash = 0
    process_total = 4
proces = []
#run_bash = 0
import swhevc_driver as process_env

class env_pool:
    class env:
        def __init__(self,id):
            self.status = 1
            self.id = id

        def access_ok(self):
            self.status = 1

        def not_access_mark(self):
            self.status = 0

        def if_access(self):
            return self.status

        def get_env_id(self):
            return self.id

    def __init__(self,bash_run_env,total=8):
        print "bash_run_env:::",bash_run_env
        self.bash_run_env = bash_run_env
        if os.path.exists(self.bash_run_env):
            shutil.rmtree(self.bash_run_env)
        self.total = total
        self.envs = []
        for i in range(0,total):
            env = self.env(i)
            self.envs.append(env)
        print "total:::",total

    def get_env_by_id(self,id):
        return self.envs[id]

    def get_env(self):
        self.reload_env()
        ret = -1
        for env in self.envs:
            
            if env.if_access():
                ret = env.get_env_id()
                self.prepare_env(ret)
                break
        return ret

    def prepare_env(self,id):

        go_to = self.bash_run_env
        if not os.path.exists(go_to):
            os.mkdir(go_to)
        env_path = go_to+"/procenv" + str(id)
        if not os.path.exists(env_path):
            os.mkdir(env_path)
        else:
            print "[error]...env id is wrong"
    def reload_env(self):
        #给每个环境设置当前状态
        go_to = self.bash_run_env

        if os.path.exists(go_to):
            for i in range(0,self.total):
                env_path = go_to+"/procenv"+str(i)
                if os.path.exists(env_path):
                    self.get_env_by_id(i).not_access_mark()
                else:
                    self.get_env_by_id(i).access_ok()
        else:
            print "not exist..."
            #time.sleep(100)






def proc(instance,queueInfo,run_bash_id):
    org_cwd = os.getcwd()

    #qid = queueInfo["queId"]%n
    bash = queueInfo["bash"]
    run_bash_dir = queueInfo["bash_run_dir"]
    bs_path = queueInfo["bs_path"]
    title = queueInfo["bash_title"]
    env_id = queueInfo["env_id"]

    os.chdir(run_bash_dir)
    #print "     >> go to cwd :", run_bash_dir
    #创建临时运行空间
    p1 =  ".runlog"+str(run_bash_id)
    p2 = p1+"/procenv"+str(env_id)
    if not os.path.exists(p1):
        while 1:
            print "[error] ",run_bash_dir+p1," not exist"
            #time.sleep(2)
    if not os.path.exists(p2):
        while 1:
            print "[error] ",p2," not exist"
            #time.sleep(2)
    os.chdir(p2)
    #print os.getcwd()
    #拷贝tbcfg
    shutil.copyfile(run_bash_dir + "/"+title, title)
    #拷贝其他
    # shutil.copyfile(run_bash_dir+"/encoder_randomaccess_main.cfg","./encoder_randomaccess_main.cfg")
    # shutil.copyfile(run_bash_dir+"/lcevc_decoder_sample","./lcevc_decoder_sample")
    cmd = "chmod -R -f 775 "+run_bash_dir
    #print cmd
    os.system(cmd)
    
    #cmd = "ls -al"
    #print cmd
    os.system(cmd)
    time.sleep(3)
    bash = bash.strip("\n") +" >bash.log 2>&1"
    print bash
    os.system(bash)
    #os.remove(title)
    #time.sleep(1)
    #根据c模型生成的文件自定义
    #这些都是生成在当前运行目录下的文件
    out_files = ["bash.log","recon.yuv"]
    os.chdir(org_cwd)
    print "bs_path bs_path bs_path bs_path ",bs_path
    print "bs_path bs_path bs_path bs_path ",bs_path
    print "bs_path bs_path bs_path bs_path ",bs_path
    print "bs_path bs_path bs_path bs_path ",bs_path
    print "bs_path bs_path bs_path bs_path ",bs_path
    #time.sleep(10)
    # do recon check
    if os.path.exists(run_bash_dir+"/"+p2+"/recon.yuv"):
        process_env.do_recon_check(instance, platform, run_bash_dir+"/"+p2+"/recon.yuv",bs_path.split("/")[-1] + ".yuv", save_recon_yuv_flag=1)


    #其他文件拷贝
    bash_logpath=instance.mkdir_in_workspace("bash_log")
    if os.path.exists(run_bash_dir+"/"+p2+"/bash.log"):
        shutil.copyfile(run_bash_dir+"/"+p2+"/bash.log",bash_logpath+"/"+bs_path.split("/")[-1]+".log")

    #删除env
    if os.path.exists(run_bash_dir+"/"+p2):
        shutil.rmtree(run_bash_dir+"/"+p2)


def prepare(instance,Lock,yuv_manager,run_queue,env_pool):
    id = 0
    max_wait_times=2
    ok=1
    while 1:
        #process_env.RebootCfg(instance)
        yuv_manager.reboot_testlist_env_status()
        end_flag = yuv_manager.get_end_flag()
        if end_flag != 1:
            #print "**********new turn start********"
            in_paths = yuv_manager.get_current_testfile()
            #print (in_paths)
            #print cwd
            if instance.get_out_change_testlist_flag():
                print "[TESTLIST CHANGE]new yuv", in_paths
            Lock.acquire()
            param = process_env.ModifyDefaultCfg(instance, in_paths)

            file_path = param["sh_file_name"]
            sh_bash_dir = param["sh_bash_dir"]
            file = open(file_path, "r")
            co = file.read()
            file.close()
            cmds = process_env.load_cmdline(co)
            bs_path = cmds["-b"]
            bash_title = cmds["title"]
            env_id = env_pool.get_env()
            
            time_counter=0
            while env_id < 0:
                print "wait for access env ..."
                time.sleep(2)
                time_counter+=1
                if time_counter >= max_wait_times :
                    print "counter ...",time_counter
                    ok=0
                    break
                env_id = env_pool.get_env()
            print "get env_id::",env_id
            queueInfo = {
                "bash": co,
                "bs_path": bs_path,
                "bash_run_dir": sh_bash_dir,
                "queId": id,
                "bash_title":bash_title,
                "env_id":env_id
            }

            while ok:
                if not run_queue.full():
                    run_queue.put(queueInfo)
                    print "[!!!]put in queue"
                    print "[!!!]put in queue"
                    print "[!!!]put in queue"
                    print "[!!!]put in queue"
                    id += 1
                    process_env.UpdateCfg(instance)
                    break
                else:
                    print "wait"
                    time.sleep(1)
            #time.sleep(2)
            Lock.release()
        else:
            print "close prepare..."
            break
    print "prepare down...ok=",ok

def prepare_one(instance,Lock,yuv_manager,run_queue,env_pool):
    id = 0
    max_wait_times=2
    ok=1
    if 1:
        #process_env.RebootCfg(instance)
        yuv_manager.reboot_testlist_env_status()
        end_flag = yuv_manager.get_end_flag()
        if end_flag != 1:
            #print "**********new turn start********"
            in_paths = yuv_manager.get_current_testfile()
            #print (in_paths)
            #print cwd
            if instance.get_out_change_testlist_flag():
                print "[TESTLIST CHANGE]new yuv", in_paths
            Lock.acquire()
            param = process_env.ModifyDefaultCfg(instance, in_paths)

            file_path = param["sh_file_name"]
            sh_bash_dir = param["sh_bash_dir"]
            file = open(file_path, "r")
            co = file.read()
            file.close()
            print co
            cmds = process_env.load_cmdline(co)
            
            bs_path = cmds["-o"]
            print bs_path
            bash_title = cmds["title"]
            env_id = env_pool.get_env()
            
            time_counter=0
            while env_id < 0:
                print "wait for access env ..."
                time.sleep(2)
                time_counter+=1

                env_id = env_pool.get_env()
            print "get env_id::",env_id
            queueInfo = {
                "bash": co,
                "bs_path": bs_path,
                "bash_run_dir": sh_bash_dir,
                "queId": id,
                "bash_title":bash_title,
                "env_id":env_id
            }

            while ok:
                if not run_queue.full():
                    run_queue.put(queueInfo)
                    print "[!!!]put in queue"
                    print "[!!!]put in queue"
                    print "[!!!]put in queue"
                    print "[!!!]put in queue"
                    id += 1
                    process_env.UpdateCfg(instance)
                    break
                else:
                    print "wait"
                    time.sleep(1)
            #time.sleep(2)
            Lock.release()
        
    print "prepare down...ok=",ok




if __name__ == "__main__":


    # 1:open envronment
    instance = process_env.open_env(platform, cwd,set_space_name_suffix="",bash_id=run_bash)
    
    # 2.set src env
    process_env.boot_src_env(platform)

    # 3:get yuv_manager from ENV instance (instance is <workspace_utils> class object)
    yuv_manager = instance.get_testlist_manager_instance()

    # 4 .run
    runlog_path = process_env.get_cmodel_path(instance)+"/.runlog"+str(run_bash)
    print "runlog_path::",runlog_path
    Lock = threading.Lock()
    _env_pool = env_pool(runlog_path,total=process_total)
    run_queue = Queue(maxsize=process_total)

    if process_total > 1 :
        print "not support now."
        time.sleep(1000)
        prep = threading.Thread(target=prepare, args=(instance,Lock,yuv_manager,run_queue,_env_pool,))
        prep.start()
        
        #如果queue不为空，则开启一个线程执行当前
        while 1:

            #time.sleep(3)
            if not run_queue.empty():
                #Lock.acquire()
                print run_queue.qsize()
                print "proc"
                print "proc."
                print "proc.."
                print "proc..."
                queueInfo = run_queue.get()
                print queueInfo
                p = Process(target=proc,args=(instance,queueInfo,run_bash,))
                proces.append(p)
                p.start()

                if run_queue.empty() and yuv_manager.get_end_flag():
                    break
                #Lock.release()
            elif run_queue.empty() and yuv_manager.get_end_flag():
                break


        prep.join()

        for pt in proces:
            pass
            pt.join()


        print "close .....   dir:::",cwd+"/.runlog"+str(run_bash)
    else:
        #while 1:
        #prepare_one(instance,Lock,yuv_manager,run_queue,_env_pool)
        print run_queue.qsize()
        print "proc"
        print "proc."
        print "proc.."
        print "proc..."
        queueInfo = run_queue.get()
        print queueInfo
        #proc(instance,queueInfo,run_bash)
            # if run_queue.empty() and yuv_manager.get_end_flag():
            #     break
    #time.sleep(100)
        print "down one"
        
    
    
    if os.path.exists(runlog_path):
        shutil.rmtree(runlog_path)

    #print "this env end..."
    process_env.close_env(platform,run_bash)
