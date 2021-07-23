#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/core/types.hpp>
#include <iostream>
#include <stdio.h>
#include <deque>
#include <chrono>
#include <vector>

void writeOut(std::deque<cv::Mat> &streamQueue)
{
    //TODO: Make this something that actually does something instead of deallocating the memory
    streamQueue.clear();
}

bool motionDetection(std::deque<cv::Mat> &streamQueue, cv::Mat &frame, cv::Mat &background)
{
    bool motion = false;
    while ( streamQueue.empty() ) { /* Wait for a frame to enter the queue. */ }
    frame = streamQueue.back();
    
    cv::Mat gray = cv::cvtColor(frame, cv::COLOR_BGR2GRAY);
    gray = cv::GaussianBlur(gray, (21, 21), 0);
    
    // Difference between static background
    cv::Mat Diff;
    cv::absdiff(background, gray, Diff);

    // If change in between static background and current frame is greater than 30 it will show white color(255)
    cv:Mat ThreshOut;
    double diffVal = cv::threshold(Diff, ThreshOut, 30, 255, cv::THRESH_BINARY)
    cv::Mat dilateOut;
    cv::dilate(ThreshOut, dilateOut, cv::Mat(), iterations=2);

    // Finding contour of moving object
    std::vector<std::vector<cv::Point>> contours;
    std::vector<cv::Vec4i> hierarchy;
    cv::findContours(dilateOut, contours, hierarchy, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);

    for (size_t i = 0; i < contours.Size(); ++i)
    {
        if ( cv::contourArea(contours[i]) < 10000 ) continue;
        motion = true;

        cv::Rect bound = cv::boundingRect(contours[i]);
        // making green rectangle arround the moving object
        cv::Point pt1 = cv::Point(bound.x, bound.y);
        cv::Point pt2 = cv::Point(bound.x + bound.w, bound.y + bound.h);
        cv::Scalar green = cv::Scalar(0, 255, 0);
        cv::rectangle(frame, pt1, pt2, green, 3);
    }

    return motion;
}


int main() 
{

    return 0;
}