
from multiprocessing import Process
from Queue import Queue
import time
import threading

class recon_check:
    def __init__(self):
        self._yuv_info = None
        self._yuv_process = None
        self._multi_instance = None
    def INIT_RECON_ENV(self,yuv_info_dict):
        self._yuv_info = self.yuv_info(path=yuv_info_dict["path"],stride=yuv_info_dict["stride"],width=yuv_info_dict["width"],height=yuv_info_dict["height"],frame_count=yuv_info_dict["frame_count"])
        self._yuv_process = self.yuv_process(self._yuv_info)
        self._multi_instance = self.MyProcess(self._yuv_process)
    def GET_MULTI_INSTANCE(self):
        if self._multi_instance is not None:
            return self._multi_instance
        else:
            print "[error]please INIT_RECON_ENV first... "
    



    class yuv_info:
        def __init__(self,path,stride,width,height,frame_count,color_format="yuv420",pixelformat="nv12"):
            self.path = path
            self.stride = stride
            self.width = width
            self.height = height
            self.frame_count = frame_count
            self.color_format = color_format
            self.pixelformat = pixelformat

        def get_yuv_path(self):
            return self.path
        def get_yuv_frame_count(self):
            return self.frame_count
        def get_frame_size(self):
            size = 0
            if self.color_format == "yuv420" :
                size = self.stride*self.height*3/2
            else:
                print "[error]not support color format..."
            return size


    class yuv_process:
        def __init__(self,yuv_info):
            self.yuv_info = yuv_info



        def get_yuv_info(self):
            return self.yuv_info
        def get_recon_frame_by_number(self,frame_num):
            fd = open(self.yuv_info.get_yuv_path(),"rb")
            frame_size = self.yuv_info.get_frame_size()
            _offset = frame_num*frame_size
            fd.seek(0, 2)
            fd_size = fd.tell()
            if _offset>fd_size:
                _offset = fd_size
            fd.seek(_offset,0)
            frame = fd.read(frame_size)
            fd.close()
            return frame

        def get_recon_md5_by_frame_number(self,frame_num):
            import md5_tools
            frame = self.get_recon_frame_by_number(frame_num)
            return md5_tools.get_md5(frame)

        def get_md5_by_frame_buffer(self,frame_buffer):
            import md5_tools
            return md5_tools.get_md5(frame_buffer)

        def get_md5_by_frame_file(self,file):
            import md5_tools
            return md5_tools.get_file_md5(file)

        def get_yuv_frames_md5(self):
            pass

    class MyProcess:
        def __init__(self,yuv_process):
            self.yuv_process = yuv_process
            self.yuv_frame_count = self.yuv_process.get_yuv_info().get_yuv_frame_count()
            self.yuv_counter = 0
            self.threads = []

        def queue_in(self,queue):
            while 1:
                while queue.full():
                    #time.sleep(10)
                    continue
                    print "[queue_in]wait for queue access availablely..."
                frame_co = self.yuv_process.get_recon_frame_by_number(self.yuv_counter)
                print "[queue_in]put frame",self.yuv_counter," into queue..."
                self.yuv_counter+=1
                queue.put(frame_co)
                if self.__CHECK_YUV_RUNOUT__(1):
                    break
            print "[queue_in]down..."

        def queue_out(self,queue,output_path):
            md5_str = ""
            counter = 0
            while 1:
                while queue.empty():
                    #time.sleep(10)
                    continue
                    print "[queue_out]wait for queue access availablely..."
                frame_co = queue.get()
                
                #test code:md5 check 
                """
                per_fname = output_path+"_"+str(counter)+".yuv"
                per_of = open(per_fname,"wb")
                per_of.write(frame_co)
                per_of.close()
                counter+=1
                
                _md5_str1 = self.yuv_process.get_md5_by_frame_file(per_fname)
                """
                _md5_str = self.yuv_process.get_md5_by_frame_buffer(frame_co)
                #If there are too many frames, you need to consider the memory problem
                md5_str += _md5_str
                print "[queue_out]md5_str:",_md5_str

                if self.__CHECK_YUV_RUNOUT__(queue.empty()):
                    break
            of = open(output_path,"w")
            print "[queue_out]write output_path:",output_path
            of.write(md5_str)
            of.close()
            print "[queue_in]down..."

        def __CHECK_YUV_RUNOUT__(self,flag):
            #yuv_counter start from 1
            if (self.yuv_counter>self.yuv_frame_count) and flag:
                return True
            else:
                #time.sleep(2)
                return False
        def prepareFrame(self,queue):
            #prepare = Process(target=self.queue_in,args=(queue,))
            prepare = threading.Thread(target=self.queue_in, args=(queue,))
            self.threads.append(prepare)

        def processFrame(self,queue):
            #process = Process(target=self.queue_out,args=(queue,))
            if hasattr(self,"output_path"):
                output_path = getattr(self,"output_path")
            else:
                #use default
                output_md5_file_name = self.yuv_process.get_yuv_info().get_yuv_path().split("/")[-1]+".md5"
                print "[processFrame]output_md5_file_name:",output_md5_file_name
                output_path = output_md5_file_name
            process = threading.Thread(target=self.queue_out, args=(queue,output_path))
            self.threads.append(process)

        def proc(self,queuesize=2):
            print ">>>>[RECON CHECK]<<<< START"
            que = Queue(maxsize=queuesize)
            self.prepareFrame(que)
            self.processFrame(que)

            for i in range(0,len(self.threads)):
                self.threads[i].start()
            #del threads
            for i in range(0,len(self.threads)):
                self.threads[i].join()
            print ">>>>[RECON CHECK]<<<< DOWN"
            #time.sleep(10)

#sample
"""
if __name__ == '__main__':
    my_yuv_info = {
        "path":"out.yuv",
        "stride":2688,
        "width":2688,
        "height":1944,
        "frame_count":28
    }
    recon_check_obj = recon_check()
    recon_check_obj.INIT_RECON_ENV(my_yuv_info)
    inst = recon_check_obj.GET_MULTI_INSTANCE()
    inst.proc()
"""