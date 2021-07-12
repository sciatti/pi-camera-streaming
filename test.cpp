//test.cpp
#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/highgui.hpp>
#include <iostream>
#include <stdio.h>
#include <deque>
#include <thread>
using namespace cv;
using namespace std;

bool stop;

void runCam()
{
    deque<Mat> streamQueue;
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
        cerr << "ERROR! Unable to open camera\n";
        return;
    }
    cap.set(cv::CAP_PROP_FRAME_WIDTH, 640.0);
    cap.set(cv::CAP_PROP_FRAME_HEIGHT, 480.0);
    cap.set(cv::CAP_PROP_FPS, 30);
    //--- GRAB AND WRITE LOOP
    cout << "Start grabbing" << endl
        << "Press any key to terminate" << endl;
    while ( !stop )
    {
        // wait for a new frame from camera and store it into 'frame'
        cap.read(frame);
        // check if we succeeded
        if (frame.empty()) {
            cerr << "ERROR! blank frame grabbed\n";
            break;
        }
        // append frame to queue
        streamQueue.push_back(frame);
        //imwrite("Live.jpg", frame);
        //return 0;
        //if (waitKey(5) >= 0)
            //break;
    }
    cout << "Frames Expected: " << 5 * 30 << " Frames Gathered: " << streamQueue.size() << "\n";
    // the camera will be deinitialized automatically in VideoCapture destructor
    //return 0;
}


int main(int, char**)
{
    stop = false;
    std::thread cameraThread (runCam);
    cameraThread.detach();
    std::this_thread::sleep_for(std::chrono::seconds(5));
    stop = true;
    std::this_thread::sleep_for(std::chrono::seconds(1));
    return 0;
}