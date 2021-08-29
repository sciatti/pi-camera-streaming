#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/core/types.hpp>
#include <opencv2/imgproc.hpp>
#include <iostream>
#include <vector>
#include <string>
#include "tsqueue.h"
#include <deque>
#include <sys/socket.h>
#include <thread>
#include <arpa/inet.h>	//inet_addr

// Videostreaming class that I will create using opencv

class videostream
{
    public:
        videostream(); // Default Constructor
        videostream(float height, float width, float fps, int index, struct sockaddr_in server); // Initialize with fps and resolution arguments
        void run(); // Function To Begin Streaming From The Camera
        bool motion(cv::Mat &frame, cv::Mat &background); // Function To Detect Motion From The Camera Stream
        void motionDetection(); // Main Motion Detection Function
        bool available(); // Return true if queue is not empty
        cv::Mat popImage(); // Return last element in the queue
        void writeVideo(std::deque<cv::Mat> &frameQueue); // Write out the data
        void sendVideo(std::deque<cv::Mat> &frameQueue); // Send the data
        //void writeVideo(Tsqueue<cv::Mat> &frameQueue); // Write out the data
        void stop(); //stop recording
        void printSummary(int sleepTime, int fpsTarget); // Print out the final stats
    private:
        std::vector<float> dims;
        std::vector<std::deque<cv::Mat>> writeVec; // vector of deques of mats that hold all the data we're gonna write out
        //std::vector<Tsqueue<cv::Mat>> writeVec; // vector of deques of mats that hold all the data we're gonna write out
        std::vector<std::string> writeNames; // vector of strings that store the write out file name
        //cv::VideoCapture cameraStream; // initialize a video capture object to stream the feed from
        //std::deque<cv::Mat> streamQueue; // initialize a queue object to store the stream feed in sequential order
        Tsqueue<cv::Mat> streamQueue; // initialize a queue object to store the stream feed in sequential order
        bool stopValue; // stop value that determines when the stream ends
        int captureIndex;
        struct sockaddr_in server_data;
};