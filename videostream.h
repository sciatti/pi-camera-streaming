#include <opencv2/opencv.hpp>
#include <iostream>
#include <deque>

// Videostreaming class that I will create using opencv

class videostream
{
    public:
        videostream(); // Default Constructor
        videostream(float height, float width, float fps); // Initialize with fps and resolution arguments
        void run(); // Function To Begin Streaming From The Camera
        bool available(); // Return true if queue is not empty
        cv::OutputArray getLastImage(); // Return last element in the queue
    private:
        cv::VideoCapture cameraStream; // initialize a video capture object to stream the feed from
        std::deque<cv::OutputArray> streamQueue; // initialize a queue object to store the stream feed in sequential order
}