#-*-coding:utf-8*-
import os,operator,shutil,json
class group_cfg:
    def __init__(self,group_path,env,json_file="__group_confiuration__.json",cfg=None):
        self.env_path = group_path+"/"+env
        self.json_file = json_file
        self.all_use_py_flag = 0
        self.env_name = env

        #得到self.group
        file = open(json_file,"rb")
        self.group = json.load(file)
        file.close()

        #setattr(self, "group_configured_by", self.group["group_configured_by"])
        #setattr(self, "group_global_params", self.group["group_global_params"])
        #setattr(self, "group_fixed_mem_config", self.group["group_fixed_mem_config"])
        self.__set_group_global()
        self.__gen_groupenv_markInfo()

    def gen_markInfo_jsonfile(self,workspace=""):
        marks = self.env["mark"]
        file_path = self.env_path+"/"+workspace+"/markInfo.json"
        file = open(file_path, "w")
        json.dump(marks,file)
        file.close()
    def __gen_groupenv_markInfo(self):
        use_cfgpy = self.all_use_py_flag
        envs = self.group["envs"]
        match = 0
        for check_env in envs:
            if check_env["env_name"] == self.env_name:
                match = 1
                self.env = check_env
                setattr(self,"env",self.env)
                break
        if not match:
            print "[Error]env:", self.env_name, " is not registered..."
            print "[Error]please check <<testenv_confiuration.json>>..."
            exit(0)
        env_configured_by = self.env["env_configured_by"]
        if (env_configured_by == "json") and (not use_cfgpy):
            setattr(self, "mark", self.env["mark"])
            setattr(self,"env_param",self.env["env_params"])
            if self.env.has_key("id_ignore_marks"):
                setattr(self,"id_ignore_marks",self.env["id_ignore_marks"])
            else:
                setattr(self, "id_ignore_marks",[])
        elif env_configured_by == "py" or use_cfgpy :
            mark = cfg

    def __set_group_global(self):
        all_use_py = self.group["group_configured_by"]
        if all_use_py == "py":
            self.all_use_py_flag = 1
        if self.group.has_key("group_global_params"):
            self.global_param= self.group["group_global_params"]
            setattr(self,"global_param",self.global_param)
        if self.group.has_key("group_fixed_mem_config"):
            self.fixed_mem_config= self.group["group_fixed_mem_config"]
            setattr(self,"fixed_mem_config",self.fixed_mem_config)

def resovle_json(file_path,key):
    key = str(key)
    file = open(file_path,"rb")
    fileJson = json.load(file)
    file.close()
    #print fileJson
    value = fileJson[key]
    return value


