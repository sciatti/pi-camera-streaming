#include "videostream.h"
/*
#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/core/types.hpp>
#include <opencv2/imgproc.hpp>
*/

//g++ -std=c++17 testMotDet.cpp videostream.cpp videostream.h tsqueue.h -o testMotDet.exe -lpthread `pkg-config --cflags --libs opencv`

void runCam(videostream &stream) 
{
    stream.run();
}

void runDetect(videostream &stream)
{
    stream.motionDetection();
}

int main(int argc, char** argv)
{
//  -------------------------------------------------------------
    struct sockaddr_in server;
    server.sin_addr.s_addr = inet_addr(argv[1]);
	server.sin_family = AF_INET;
	server.sin_port = htons( 12345 );

//  -------------------------------------------------------------

    // Initialize The Stream Object
    videostream stream(640.0, 480.0, 20.0, 0, server);
    // Give the stream a separate thread of execution and set it to run
    std::thread cameraThread (runCam, std::ref(stream));
    cameraThread.detach();
    
    // Set up the Motion Detection Code
    std::thread motionThread (runDetect, std::ref(stream));
    motionThread.detach();

    //std::this_thread::sleep_for(std::chrono::seconds(2));
    std::cout << "Enter Anything To Stop Detection: ";
    std::string input;
    std::cin >> input;
    stream.stop();
    std::deque<cv::Mat> a;
    //stream.writeVideo(a);

    return 0;
}

