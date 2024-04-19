#include "sevc_baseenc.h"


int get_base_recon(unsigned char *y, unsigned char *u, unsigned char *v, unsigned char *y_recon, unsigned char *u_recon, unsigned char *v_recon,int w,int h){
    // // 读取一个YUV
    printf("enter get_base_recon %dx%d\n",w,h);

    char command[200];
    sprintf(command, "./modules/baseenc/src/TAppEncoderStatic -c ./modules/baseenc/src/encoder_intra_main.cfg -c ./modules/baseenc/src/sequence.cfg");
    system(command);

    FILE* fp = fopen("rec.yuv", "rb");
    fread(y_recon, 1, w * h , fp);
    fread(u_recon, 1, w * h / 4, fp);
    fread(v_recon, 1, w * h / 4, fp);
    //stride！！！！
    fclose(fp);

    // // + test real-time
    // y_recon = y;
    // u_recon = u;
    // v_recon = v;
    // // - test real-time
    return 0;
}