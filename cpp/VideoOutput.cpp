#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/highgui.hpp>
#include <iostream>
#include <stdio.h>
#include <deque>
#include <chrono>
using namespace cv;

// Sample Video Writing File

void writeOut()
{
    time_t timer;
    std::deque<Mat> streamQueue;
    Mat frame;
    //--- INITIALIZE VIDEOCAPTURE
    VideoCapture cap;
    // open the default camera using default API
    // cap.open(0);
    // OR advance usage: select any API backend
    int deviceID = 0;             // 0 = open default camera
    int apiID = cv::CAP_ANY;      // 0 = autodetect default API
    // open selected camera using selected API
    cap.open(deviceID, apiID);
    // check if we succeeded
    if (!cap.isOpened()) {
        std::cerr << "ERROR! Unable to open camera\n";
        return;
    }
    cap.set(cv::CAP_PROP_FRAME_WIDTH, 640.0);
    cap.set(cv::CAP_PROP_FRAME_HEIGHT, 480.0);
    cap.set(cv::CAP_PROP_FPS, 30);

    while ( !cap.read(frame) ) 
    {
     //wait until capture returns correctly
    }

    int duration = 60;
    
    auto begin = std::chrono::steady_clock::now();
    auto start = std::chrono::steady_clock::now();
    int lastVal = 0;
    for (int i = 0; i < duration * 30; ++i){
        if ( cap.read(frame) ) streamQueue.push_back(frame);
        std::chrono::duration<double> diff = std::chrono::steady_clock::now() - start;
        if ( diff.count() > 10.0 ) {
            std::cout << i - lastVal << " frames gathered in " << diff.count() << " seconds.\n";
            start = std::chrono::steady_clock::now();
            lastVal = i;
        }
    }
    std::chrono::duration<double> diff = std::chrono::steady_clock::now() - begin;
    std::cout << "Frame Gathering Complete.\n" << duration * 30 << " frames gathered in " << diff.count() << " seconds.\n";

    VideoWriter v;
    v.open("testWrite.avi", VideoWriter::fourcc('H', '2', '6', '4'), 30, Size(640, 480));

    while ( !streamQueue.empty() )
    {
        v.write(streamQueue.front());
        streamQueue.pop_front();
    }
}

int main()
{
    writeOut();
}