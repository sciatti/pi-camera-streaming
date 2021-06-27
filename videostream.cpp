#include "videostream.h"
// Implementation for the videostream class that I will develop using opencv


videostream::videostream(float height, float width, float fps)
{
    cameraStream.set(cv::CAP_PROP_FRAME_WIDTH, width);
    cameraStream.set(cv::CAP_PROP_FRAME_HEIGHT, height);
    cameraStream.set(cv::CAP_PROP_FPS, fps);
}

void videostream::run()
{
    return
}
bool videostream::available()
{
    return streamQueue.size() > 0;
}
cv::OutputArray videostream::getLastImage()
{
    return streamQueue.pop();
} 