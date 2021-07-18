#include "videostream.h"
#include <thread>

//g++ FRT.cpp videostream.cpp videostream.h -o FRT -lpthread `pkg-config --cflags --libs opencv`

void basic(videostream v)
{
    v.run();
}

int main() {
    videostream vid(480.0, 640.0, 30.0, 0);
    std::thread cameraThread (basic, vid);
    cameraThread.detach();
    std::this_thread::sleep_for(std::chrono::seconds(5));
    vid.stop();
    //cameraThread.join();
    vid.printSummary(5, 30);
    return 0;
}