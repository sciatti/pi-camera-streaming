#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/core/types.hpp>
#include <opencv2/imgproc.hpp>
// #include <opencv2/opencv.hpp>
#include <raspicam/raspicam_cv.h>
#include <iostream>
#include <stdio.h>
#include <deque>
#include <chrono>
#include <vector>
#include <thread>
#include <string>

//g++ motionDetectionTest.cpp -o motDet.exe -I/usr/local/include/ -lraspicam -lraspicam_cv -lmmal -lmmal_core -lmmal_util -lopencv_core -lopencv_highgui `pkg-config --cflags --libs opencv` -L/opt/vc/lib -lmmal

void writeOut(std::deque<cv::Mat> &streamQueue)
{
    //TODO: Make this something that actually does something instead of deallocating the memory
    streamQueue.clear();
}

//bool motionDetection(std::deque<cv::Mat> &streamQueue, cv::Mat &frame, cv::Mat &background)
bool motionDetection(cv::Mat &frame, cv::Mat &background)
{
    bool motion = false;
//    while ( streamQueue.empty() ) { /* Wait for a frame to enter the queue. */ }
//    frame = streamQueue.back();
    
    cv::Mat gray;
    //cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);
    cv::GaussianBlur(gray, gray, cv::Size(21, 21), 0);
    
    // Difference between static background
    cv::Mat Diff;
    cv::absdiff(background, gray, Diff);

    // If change in between static background and current frame is greater than 30 it will show white color(255)
    cv::Mat ThreshOut;
    double diffVal = cv::threshold(Diff, ThreshOut, 30, 255, cv::THRESH_BINARY);
    cv::Mat dilateOut;
    cv::dilate(ThreshOut, dilateOut, cv::Mat(), cv::Point(-1,-1), 2);

    // Finding contour of moving object
    std::vector<std::vector<cv::Point>> contours;
    std::vector<cv::Vec4i> hierarchy;
    cv::findContours(dilateOut, contours, hierarchy, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);

    for (size_t i = 0; i < contours.size(); ++i)
    {
        if ( cv::contourArea(contours[i]) < 10000 ) continue;
        motion = true;

        cv::Rect bound = cv::boundingRect(contours[i]);
        // making green rectangle arround the moving object
        cv::Point pt1 = cv::Point(bound.x, bound.y);
        cv::Point pt2 = cv::Point(bound.x + bound.width, bound.y + bound.height);
        //cv::Scalar green = cv::Scalar(0, 255, 0);
        cv::Scalar black = cv::Scalar(0, 0, 0);
        cv::rectangle(frame, pt1, pt2, black, 3);
    }

    return motion;
}

void driver()
{
    std::deque<cv::Mat> streamQueue;
    cv::Mat frame;
    cv::Mat frame2;
    cv::Mat backGround;
    //cv::VideoCapture cap;
    raspicam::RaspiCam_Cv cap;
    // open the default camera using default API
    int deviceID = 0;             // 0 = open default camera
    int apiID = cv::CAP_ANY;      // 0 = autodetect default API
    // open selected camera using selected API
    cap.set( cv::CAP_PROP_FORMAT, CV_8UC1 );
    //cap.open(deviceID, apiID);
    // check if we succeeded
    //if (!cap.isOpened())
    if ( !cap.open() )
    {
        std::cerr << "ERROR! Unable to open camera\n";
        return;
    }
    //cap.set(cv::CAP_PROP_FRAME_WIDTH, 640.0);
    //cap.set(cv::CAP_PROP_FRAME_HEIGHT, 480.0);
    //cap.set(cv::CAP_PROP_FPS, 30);

    if ( !cap.grab() ) 
    {
        std::cerr << "ERROR! Unable to read from camera\n";
    }
    cap.retrieve(backGround);
    //cv::cvtColor(backGround, backGround, cv::COLOR_BGR2GRAY);
    cv::GaussianBlur(backGround, backGround, cv::Size(21, 21), 0);

    std::string input;
    int duration = 3;
    int count = 0;
    std::cout << "Type 'quit' to quit, else type anything to record a frame:";
    while ( std::cin >> input ) 
    {
        if ( input == "quit" ) break;
        std::cout << "\n";
        for (int i = 0; i < duration; ++i)
        {
            std::cout << "Reading a frame in " << duration - i << " seconds...\n";
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
        std::cout << "Reading Frame Now...\n";
        /*if ( count >= 1 ) {
            cap.grab();
            cap.retrieve(frame2);
            std::string fname = "static" + std::to_string(count) + ".png";
            cv::imwrite(fname, frame2);
            return;
        }*/
        if ( cap.grab() ) 
        {
            cap.retrieve(frame);
            if (frame.empty()) {
                std::cerr << "ERROR! blank frame grabbed\n";
                return;
            }
            //std::string fname = "static" + std::to_string(count) + ".png";
            //cv::imwrite(fname, frame);
            streamQueue.push_back(frame);
            count++;
            //std::cerr << "ERROR! Unable to open camera\n";
            //return;
        }
        else 
        {
            std::cout << "Error Reading Frame\n";
        }
        std::cout << "Type 'quit' to quit, else type anything to record a frame:";
    }
    std::cout << "There were " << count << " reads on the camera\n";
    /*return;
    for (int i = 0; i < streamQueue.size(); i++) 
    {
        auto fr = streamQueue.front();
        std::string fname = "static" + std::to_string(i) + ".png"; 
        cv::imwrite(fname, fr);
        streamQueue.pop_front();
    }*/
    for (int i = 0; i < streamQueue.size(); i++) 
    {
        auto fr = streamQueue.front();
        auto start = std::chrono::steady_clock::now();
        bool x = motionDetection(fr, backGround);
        std::chrono::duration<double> diff = std::chrono::steady_clock::now() - start;
        std::cout << "motionDetection() output: " << x << " duration: " << diff.count() << " seconds\n";
        std::string fname = "static/static" + std::to_string(i) + ".png"; 
        cv::imwrite(fname, fr);
        streamQueue.pop_front();
    }
    cv::imwrite("bg.png", backGround);

}

int main() 
{
    driver();
    return 0;
}