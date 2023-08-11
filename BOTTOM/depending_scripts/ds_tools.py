#-*-coding:utf-8*-
import re
import os
import sys
import glob
import filecmp
import time



class ds_5_tools:
    
    def __init__(self):   
        self.ec = None
    restore_ds_file_path = ''
    dump_ds_file_path = ''
    streamBase = 0
    _test_block_file_name = []
    _filePath = ''
    #test switch
    TestSwitch_wenjiancaijie = 0

    @staticmethod
    def get_ds5_debugger_instance():
        from arm_ds.debugger_v1 import Debugger
        from arm_ds.debugger_v1 import DebugException
        debugger = Debugger()
        #print "debugger",debugger
        ec = debugger.getCurrentExecutionContext()
        return ec
    def get_debugger_instance(self):
        if self.ec == None:
            self.ec = ds_5_tools.get_ds5_debugger_instance()
        return self.ec
    
    def _gen_dump_ds_file(self,filepath,addr_start,addr_end):
        str = "dump memory "+filepath+" "+hex(addr_start)+" "+hex(addr_end)+"\n"
        #print "_gen_dump_ds_file >>> ",str
        return str

    def dump_file_param_size(self,filepath,addr,size):
        end_addr = addr+size+1
        str = self._gen_dump_ds_file(filepath,addr,end_addr)
        #print str
        if self.dump_ds_file_path=='':
            print "[Error].... dump.ds file dose not exist..."
            exit(0)
        ds = open(self.dump_ds_file_path,"w")
        ds.write(str)
        ds.close()

    def dump_file_param_endaddr(self,filepath,addr,endaddr):
        str = self._gen_dump_ds_file(filepath,addr,endaddr)
        if self.dump_ds_file_path=='':
            print "[Error].... dump.ds file dose not exist..."
            exit(0)
        ds = open(self.dump_ds_file_path,"w")
        ds.write(str)
        ds.close()
        
    def _wirte_files(self,filePath,filename,num,s):
        filePath = filePath + "/" + filename
        output = filePath + "_"+str(num)+".out"
        out = open(output,"wb")
        out.write(s)
        out.close()
        self._test_block_file_name.append(output)
        return output

    def _gen_restore_ds_file(self,output,offset):
        add = hex(int(self.streamBase)+int(offset))
        str = "restore "+output+" "+" binary " +add+"\n"
        #print "_gen_restore_ds_file >>> ",str
        return str
    
    

    def restore_big_file(self, filePath,PerSize):  # ecP:stackFrame context ;PerSize:restore size per time
        filePath = filePath.strip("\n")
        self._filePath = filePath
        #print filePath
        out_path_blocks = filePath.strip("\n").split("/")
        #print out_path_blocks
        out_path = ""
        for i in range(0,len(out_path_blocks)-1):
            out_path += out_path_blocks[i]+"/"
        out_path = out_path+"outTag"
        print "[RESTORE]restore_big_file >>> out_path ::",out_path
        filename = filePath.split("/")[-1]
        if not os.path.exists(out_path):
            os.mkdir(out_path)
        filesize = os.path.getsize(filePath)
        rest_size = PerSize
        offset = 0
        if self.restore_ds_file_path=='':
            print "[Error].... restore.ds file dose not exist..."
            exit(0)
        infile = open(filePath,"rb")
        ds = open(self.restore_ds_file_path,"w")
        i=0
        while(rest_size < filesize):
            s = infile.read(PerSize)
            i+=1
            outputfile = self._wirte_files(out_path,filename,i,s)
            ds.write(self._gen_restore_ds_file(outputfile,offset))
            rest_size += PerSize
            offset += PerSize
            print "  >>offset:"+hex(offset)
        print " >>offset:" + hex(offset)
        s = infile.read(filesize-offset)
        i += 1
        outputfile = self._wirte_files(out_path,filename, i, s)
        ds.write(self._gen_restore_ds_file(outputfile,offset))
        infile.close()
        ds.close()
        if self.TestSwitch_wenjiancaijie == 1:
            self._merge_block_file()

    def _merge_block_file(self):
        out_path = self._filePath.strip(self._filePath.split('.')[-1])+"_cmp.out"
        out = open(out_path,"wb")
        for i in range(0,len(self._test_block_file_name)):
            cotent = open(self._test_block_file_name[i],"rb")
            cmp_cotent = open(self._test_block_file_name[i]+".cmp","wb")
            co = cotent.read(os.path.getsize(self._test_block_file_name[i]))
            out.write(co)
            out.flush()
            cmp_cotent.write(co)
            cmp_cotent.close()
            cotent.close()
        out.close()
        if filecmp.cmp(out_path,self._filePath) == False:
            #print "outputfile at:" + out_path
            while(1):
                print "[Error]check the file and program...."
                time.sleep(5)
        else:
            os.remove(out_path)

    def excute_ds_file(self,ds_file_name):
        ec = self.get_debugger_instance()
        ds = open(ds_file_name,"r") 
        ds_lines = ds.readlines()
        for ds_line in ds_lines:
            ec.executeDSCommand(ds_line) 
    
    def excute_source_script_file(self,script_file_path):
        ec = self.get_debugger_instance()
        cmd = "source /v "+script_file_path
        #print "==== >> excute_cmd ::  ",cmd
        ec.executeDSCommand(cmd) 

    #从start_addr开始向ddr写入size长的数据，该数据的值为value
    def excute_write_memory(self,fill_start_addr,fill_size,value):
        ec = self.get_debugger_instance()
        fill_end_addr = int(fill_start_addr)+int(fill_size)-1
        cmd = "memory fill "+hex(fill_start_addr)+" "+hex(fill_end_addr)+" "+str(fill_size)+" "+hex(value)
        ec.executeDSCommand(cmd) 

    def excute_cmd(self,cmd):
        ec = self.get_debugger_instance()
        ec.executeDSCommand(cmd) 