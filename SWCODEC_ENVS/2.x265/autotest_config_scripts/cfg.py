#-*-coding:utf-8*-

"""
1:配置当前环境中使用的ddr地址
"""
YUV_BASE = 0x88019000
#CFG_BASE = 0x88000000
ARGS_BASE = 0x88000000
STREAM_BASE = 0xC8019000
WTR_VALUE_ADDR_START = 0xC8A19000
FORMAT_ID_ADDR_START = 0xC8A19010
CHANGE_MAIN_TESTENV = 0xC8A19020

"""
2:配置当前编码标准
"""
#   0:h265
#   1:h264
#   2:jpeg
codec_id=0




#3.配置切换的类型，每添加一个类型名需要添加对应的遍历范围数组和参数替换规则数组
#e.g.
# 添加一个类型名到mark数组中：    mark = ["abc"]
# 对应需要添加：  1）遍历范围：    abc = [1,2,3,5]
#               2) 参数替换规则：abc_rules = [
#                                            ["--param_name1",1],  >>  表示把参数param1替换为1
#                                            ["--param_name2",abc] >>  表示把参数param2依次替换为abc数组中的值
#                                           ]
mark = [
    'constant_chroma',
    'dbk_close',
    'sao_close',
    'gdr',
    'hrd',
    'inner_clk_gate',
    'long_reference',
    'nv12',
    'rdo_level',
    'rfc',
    'sei',
    'set_offset_stride',
    'sliceSize',
    'vui'
]
#"inner_dyn_change_bitrate","inner_dyn_change_frmate","inner_dyn_change_qp","intraArea","linebuf",'roiArea_deltaQP','roiArea_roiQP','skipMap','user_data'
constant_chroma = []
dbk_close = []
sao_close = []
gdr = []
hrd = []
inner_clk_gate = []
long_reference = []
nv12 = []
rdo_level = [1,2,3]
rfc = []
sei = []
set_offset_stride = []
sliceSize = []
vui = []

constant_chroma_rules = [
    ["#--enableConstChroma",1],
    ["#--constCb",255],
    ["#--constCr",255]
]
dbk_close_rules =[
    ["--disableDeblocking",1]
    ]
sao_close_rules = [
    ["--enableSao",0]
]
gdr_rules = [
    ["#--gdrDuration",2]
]
hrd_rules  = [
    ["--bitPerSecond",300000],
    ["#--hrdConformance",1],
    ["#--cpbSize",500000],
    ["#--enableVuiTimingInfo",1]
]
inner_clk_gate_rules = [
    ["#--testId",45]
]
inner_dyn_change_bitrate_rules = [
    ["#--testId",48]
]
inner_dyn_change_frmate_rules = [
    ["#--testId",47]
]
inner_dyn_change_qp_rules = [
    ["#--testId",46]
]
intraArea_rules = [
    ["#--intraArea","1:1:3:3"]
]
linebuf_rules = [
    ["#--inputLineBufferMode",1],
    ["#--inputLineBufferDepth",4],
    ["#--inputLineBufferAmountPerLoopback",5]
]
long_reference_rules = [
    ["--intraPicRate",30],
    ["#--LTR","2:5:10"]
]
linebuf_rules = [
    ["--picRc",0],
    ["--ctbRc",0],
    ["#--fixedIntraQp",26]
]
nv12_rules = [
    ["--inputFormat",1]
] 
rdo_level_rules = [
    ["--rdoLevel",rdo_level],
    ["--enableRdoQuant",1]
]
rfc_rules = [
    ["--compressor",3]
] 
roiArea_deltaQP_rules = [
    ["#--roi1Area","0:0:4:2"],
    ["#--roi1DeltaQp",18]
]
roiArea_roiQP_rules = [
    ["#--roi1Area","0:0:4:2"],
    ["#--roi1Qp",18]
]
sei_rules = [
    ["--sei",1]
] 
set_offset_stride_rules = [
    ["--width",128],
    ["--height",74],
    ["--horOffsetSrc",64],
    ["--verOffsetSrc",16]
]
skipMap_rules = [
    
] 
user_data_rules = [
    
] 
sliceSize_rules = [
    ["--sliceSize",4]
] 
vui_rules = [
    ["--enableVuiTimingInfo",1]
]
 

