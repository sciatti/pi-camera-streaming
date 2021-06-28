#include "videostream.h"
#include <thread>

int main() {
    videostream vid(480.0, 640.0, 30.0);
    std::this_thread::sleep_for(std::chrono::seconds(5));
    vid.stop();
    return 0;
}