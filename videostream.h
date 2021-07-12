#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/highgui.hpp>
#include <iostream>
#include <deque>
#include <vector>

// Videostreaming class that I will create using opencv

class videostream
{
    public:
        videostream(); // Default Constructor
        videostream(float height, float width, float fps, int index); // Initialize with fps and resolution arguments
        void run(); // Function To Begin Streaming From The Camera
        bool available(); // Return true if queue is not empty
        cv::Mat popImage(); // Return last element in the queue
        void stop(); //stop recording
        void printSummary(int sleepTime, int fpsTarget); // Print out the final stats
    private:
        std::vector<float> dims;
        //cv::VideoCapture cameraStream; // initialize a video capture object to stream the feed from
        std::deque<cv::Mat> streamQueue; // initialize a queue object to store the stream feed in sequential order
        bool stopValue; // stop value that determines when the stream ends
        int captureIndex;
};