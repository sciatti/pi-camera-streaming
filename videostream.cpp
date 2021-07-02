#include "videostream.h"
// Implementation for the videostream class that I will develop using opencv

videostream::videostream()
{
    stopValue = true;
}

videostream::videostream(float height, float width, float fps, int index=0)
{
    stopValue = true;
    cameraStream = cv::VideoCapture(index);
    cameraStream.set(cv::CAP_PROP_FRAME_WIDTH, width);
    cameraStream.set(cv::CAP_PROP_FRAME_HEIGHT, height);
    cameraStream.set(cv::CAP_PROP_FPS, fps);
}

void videostream::run()
{
    stopValue = true; //just make sure this is right when starting... probably remove later
    std::cout << "Resolution: " << cameraStream.get(cv::CAP_PROP_FRAME_WIDTH) << cameraStream.get(cv::CAP_PROP_FRAME_HEIGHT) <<
     " @ " << cameraStream.get(cv::CAP_PROP_FPS) << " FPS\n";
    while ( stopValue ) {
        cv::Mat img;
        if ( cameraStream.read(img) ) streamQueue.push_back(img);
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