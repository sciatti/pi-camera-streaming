#include "videostream.h"
// Implementation for the videostream class that I will develop using opencv

videostream::videostream()
{
    stopValue = true;
}

videostream::videostream(float height, float width, float fps)
{
    stopValue = true;
    cameraStream.set(cv::CAP_PROP_FRAME_WIDTH, width);
    cameraStream.set(cv::CAP_PROP_FRAME_HEIGHT, height);
    cameraStream.set(cv::CAP_PROP_FPS, fps);
}

void videostream::run()
{
    stopValue = true; //just make sure this is right when starting... probably remove later
    std::cout << "Resolution: " << cameraStream.get(cv2.CAP_PROP_FRAME_WIDTH) << cameraStream.get(cv2.CAP_PROP_FRAME_HEIGHT) <<
     " @ " << cameraStream.get(cv2.CAP_PROP_FPS) << " FPS\n";
    while ( stopValue ) {

    }
}

void videostream::run()
{
    stopValue = false;
}

bool videostream::available()
{
    return streamQueue.size() > 0;
}

cv::OutputArray videostream::getLastImage()
{
    return streamQueue.pop();
} 