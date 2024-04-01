#-*-coding:utf-8*-
import json,os
import group_configuration_tool
#与自动化环境相关的
class curr_info:
    curr_cfg_name = ""
    curr_bash_path = ""

    def __init__(self, dir, platform="", bash_id=0):
        self.dir = dir
        self.platform = platform
        self.bash_id = bash_id

        self.group_cfg_obj = self.__gen_curr_group_cfg()
        # 获取当前运行的env
        
        file_name = ""
        # 该文件是上一个py执行后产生的
        self.group_cfg_obj
        # os.remove(file_name)

        s = env.split("/")[-1].split("$")
        self.running_env_name = s[0]
        self.running_env_src_type = None

        self.wp_path = None
        self.sh_path = None

        if len(s) > 1:
            self.running_env_src_type = s[1]
        self.curr_env_path = self.dir + "/" + self.running_env_name

        

    def set_wp_path(self, path):
        self.wp_path = path

    def get_cur_envs_of_group_path(self):
        return self.dir

    def get_curr_env_path(self):
        return self.curr_env_path

    def get_platform(self):
        return self.platform

    def get_curr_env_src_type(self):
        return self.running_env_src_type

    def save_bashFileName(self, FileName):
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
        return group_configuration_tool.group_cfg(group_path=self.dir, env=self.running_env_name,
                                                  json_file=self.dir + "/__group_confiuration__.json")

    def get_group_global_param(self):
        # print "global_param setting...",self.group_cfg_obj
        return getattr(self.group_cfg_obj, "global_param")

    def get_env_param(self):
        return getattr(self.group_cfg_obj, "env_param")

    def get_group_fix_mem(self):
        return getattr(self.group_cfg_obj, "fixed_mem_config")

    def get_id_ignore_marks(self):
        return getattr(self.group_cfg_obj, "id_ignore_marks")

    def gen_curr_workInfo(self, workspace=""):
        self.group_cfg_obj.gen_markInfo_jsonfile(workspace)

    def __init_curr_db_info(self):
        ret = {}
        ret["sh_path"] = self.get_bashFileName()
        ret["wp_path"] = self.wp_path
        return ret

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
        p = run_dir + "/" + name
        if not os.path.exists(run_dir):
            os.mkdir(run_dir)
        return p

    def update_curr_status_db(self):

        fpOut = open(self.__get_env_log_path(), "w")

        json.dump(self.__init_curr_db_info(), fpOut)
        fpOut.close()