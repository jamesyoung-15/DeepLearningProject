#include "test/api/m64p_common.h"
#include "test/api/m64p_frontend.h"
#include "test/api/m64p_config.h"
#include "test/api/m64p_debugger.h"
#include <iostream>
#include <fstream>

#define PIF_ROM_SIZE 2048

int main(){
    FILE *fPtr = fopen("../rom/mariokart64.n64", "rb");
    if(fPtr!=NULL){    
        fseek(fPtr, 0L, SEEK_END);
        long romlength = ftell(fPtr);
        fseek(fPtr, 0L, SEEK_SET);
        unsigned char *ROM_buffer = (unsigned char *) malloc(romlength);
        fclose(fPtr);
        std::cout << romlength <<  std::endl;
    }
    else{
        printf("Null\n");
    }


    return 0;
}