#include "videostream.h"
// Implementation for the videostream class that I will develop using opencv

videostream::videostream()
{
    stopValue = true;
}

videostream::videostream(float height, float width, float fps, int index=0)
{
    stopValue = true;
    //cameraStream = cv::VideoCapture();
    captureIndex = index;
    dims.push_back(width);
    dims.push_back(height);
    dims.push_back(fps);
    //cameraStream.set(cv::CAP_PROP_FRAME_WIDTH, width);
    //cameraStream.set(cv::CAP_PROP_FRAME_HEIGHT, height);
    //cameraStream.set(cv::CAP_PROP_FPS, fps);
}

void videostream::run()
{
    cv::VideoCapture cameraStream;
    stopValue = true; //just make sure this is right when starting... probably remove later
    cameraStream.open(0, cv::CAP_ANY);
    if ( cameraStream.isOpened() ) std::cout << "Camera Successfully Initialized\n";
    else std::cout << "Failed To Initialize Camera, Exiting...\n"; return;
    
    std::cout << "Resolution: " << cameraStream.get(cv::CAP_PROP_FRAME_WIDTH) << cameraStream.get(cv::CAP_PROP_FRAME_HEIGHT) <<
     " @ " << cameraStream.get(cv::CAP_PROP_FPS) << " FPS\n";
    while ( stopValue ) {
        cv::Mat img;
        bool ret = cameraStream.read(img);
        //std::cout << "return value: " << ret << "\n";
        if ( !img.empty() ) streamQueue.push_back(img);
    }
    //cameraStream.release();
    //cv::destroyAllWindows();
}

bool videostream::available()
{
    return streamQueue.size() > 0;
}

cv::Mat videostream::popImage()
{
    cv::Mat ret = streamQueue.back();
    streamQueue.pop_back();
    return ret;
}

void videostream::printSummary(int sleepTime, int fpsTarget)
{
    std::cout << "Frames Expected: " << sleepTime * fpsTarget << " Frames Gathered: " << streamQueue.size() << "\n";
}

void videostream::stop()
{
    stopValue = false;
}