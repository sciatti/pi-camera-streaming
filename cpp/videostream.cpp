#include "videostream.h"
// Implementation for the videostream class that I will develop using opencv

// https://stackoverflow.com/questions/20314524/c-opencv-image-sending-through-socket

videostream::videostream()
{
    stopValue = true;
    blurSize = cv::Size(9, 9);
}

videostream::videostream(float height, float width, float fps, int index, struct sockaddr_in server)
{
    stopValue = true;
    //cameraStream = cv::VideoCapture();
    captureIndex = index;
    dims.push_back(width);
    dims.push_back(height);
    dims.push_back(fps);
    blurSize = cv::Size(9, 9);
    server_data = server;
}

void videostream::run()
{
    cv::VideoCapture cameraStream;
    stopValue = true; //just make sure this is right when starting... probably remove later
    cameraStream.open(0, captureIndex);
    if ( cameraStream.isOpened() ) std::cout << "Camera Successfully Initialized\n";
    else 
    {
        std::cout << "Failed To Initialize Camera, Exiting...\n"; 
        return;
    }
    
    if ( dims.size() > 0 ) 
    {
        cameraStream.set(cv::CAP_PROP_FRAME_WIDTH, dims[1]);
        cameraStream.set(cv::CAP_PROP_FRAME_HEIGHT, dims[0]);
        cameraStream.set(cv::CAP_PROP_FPS, dims[2]);
    }
    std::cout << "Resolution: " << cameraStream.get(cv::CAP_PROP_FRAME_WIDTH) << "x" << cameraStream.get(cv::CAP_PROP_FRAME_HEIGHT) <<
    " @ " << cameraStream.get(cv::CAP_PROP_FPS) << " FPS" << " Format: " << cameraStream.get(cv::CAP_PROP_FORMAT) << "\n";
    auto st = std::chrono::system_clock::now();
    while ( stopValue ) {
        std::chrono::duration<double> diff = std::chrono::system_clock::now() - st;
        if ( diff.count() > 10.0 ) 
        {
            std::cout << "10 Seconds Have Passed. Frame Queue Size: " << streamQueue.size() << "\n";
            st = std::chrono::system_clock::now();
        }
        cv::Mat img;
        bool ret = cameraStream.read(img);
        //std::cout << "return value: " << ret << "\n";
        if ( !img.empty() ) streamQueue.push(img);//streamQueue.push_back(img);
    }
    std::cout << "Releasing Camera Stream\n";
    cameraStream.release();
    //cv::destroyAllWindows();
}

bool videostream::available()
{
    return streamQueue.size() > 0;
}

cv::Mat videostream::popImage()
{
    //cv::Mat ret = streamQueue.front();
    //streamQueue.pop_front();
    //return ret;
    return streamQueue.pop();
}

void videostream::printSummary(int sleepTime, int fpsTarget)
{
    std::cout << "Frames Expected: " << sleepTime * fpsTarget << " Frames Gathered: " << streamQueue.size() << "\n";
}

void videostream::stop()
{
    stopValue = false;
}

bool videostream::motion(cv::Mat &frame, cv::Mat &background)
{
    bool motion = false;
    cv::Mat gray;
    cv::Mat Diff;
    cv::Mat ThreshOut;
    cv::Mat dilateOut;

    cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);
    cv::GaussianBlur(gray, gray, blurSize, 0);
    
    // Difference between static background
    cv::absdiff(background, gray, Diff);

    // If change in between static background and current frame is greater than 30 it will show white color(255)
    double diffVal = cv::threshold(Diff, ThreshOut, 30, 255, cv::THRESH_BINARY);
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
        cv::Scalar green = cv::Scalar(0, 255, 0);
        //cv::Scalar black = cv::Scalar(0, 0, 0);
        cv::rectangle(frame, pt1, pt2, green, 3);
    }

    return motion;
}

void videostream::motionDetection()
{
    cv::Mat static_back;
    while ( !available() ) { }//std::this_thread::sleep_for(std::chrono::seconds(0.01)); }
    static_back = popImage();
    cv::cvtColor(static_back, static_back, cv::COLOR_BGR2GRAY);
    cv::GaussianBlur(static_back, static_back, blurSize, 0);

    // Assign the timing values and booleans
    auto stop_motion_time = std::chrono::system_clock::from_time_t(0.0);
    auto start_motion_time = std::chrono::system_clock::from_time_t(0.0);
    auto motion_time = std::chrono::system_clock::from_time_t(0.0);
    bool motion_last_frame = false;
    bool motion = false;
    bool swappedBG = false;
    cv::Mat frame;
    int videoName = 0;
    std::deque<cv::Mat> writeData;
    while ( stopValue )
    {
        // wait until the queue becomes populated
        while ( !available() ) { }//std::this_thread::sleep_for(std::chrono::seconds(0.01)); }
        frame = popImage();
        motion = videostream::motion(frame, static_back);
	if ( motion )
        {
            swappedBG = false;
            motion_time = std::chrono::system_clock::now();
            if ( !motion_last_frame ) start_motion_time = motion_time;
            std::chrono::duration<double> diff = motion_time - start_motion_time;
            if ( diff.count() > 5.0 ) 
            {
                cv::cvtColor(frame, static_back, cv::COLOR_BGR2GRAY);
                cv::GaussianBlur(static_back, static_back, blurSize, 0);
            }
            writeData.push_back(frame);
            std::cout << "appended frame from motion\n";
        }
        else
        {
            std::chrono::duration<double> diff = std::chrono::system_clock::now() - stop_motion_time;
            if ( motion_last_frame ) 
            {
                stop_motion_time = std::chrono::system_clock::now();
                std::cout << "found motion last frame\n";
                writeData.push_back(frame);
            }
            else if ( diff.count() < 0.5 )
            {
                std::cout << "appending frame from no motion\n";
                writeData.push_back(frame);
            }
            else
            {
                if ( writeData.size() > 0 )
                {
                    // Send the data to the server...
                    // Eventually we probably want to run this in a detached thread but
                    // for now it is fine to be on the same thread
                    sendVideo(writeData);
                    writeData.clear();
                    
                    // We need to write the gathered data out now...
                    //writeVec.push_back(writeData);
                    //writeNames.push_back(std::to_string(videoName));
                    //writeData.clear();
                    //videoName++;
                }
            }
        }
        motion_last_frame = motion;
    }
    std::cout << "Ending Motion Detection\n";
}

void videostream::writeVideo(std::deque<cv::Mat> &frameQueue)
{
    std::cout << "Writing Gathered Videos\n";
    for (size_t i = 0; i < writeVec.size(); ++i)
    {
        std::cout << "Writing video " << std::to_string(i) << ".avi...\n";
        cv::VideoWriter v = cv::VideoWriter(writeNames[i] + ".avi", cv::VideoWriter::fourcc('H', '2', '6', '4'), dims[2], cv::Size(dims[1], dims[0]));
        while ( !writeVec[i].empty() ) {
            v.write(writeVec[i].front());
            writeVec[i].pop_front();
        }
        std::cout << "Completed writing " << std::to_string(i) << ".avi\n";
    }
}

void videostream::sendVideo(std::deque<cv::Mat> &frameQueue)
{
    // Call this on another detached thread since it will either quit immediately after failing a connection or 
    // Run through its frames in its queue (not that many like 200 max) and quickly send them over to the server

	// Attempt to create the socket
	int socket_desc = socket(AF_INET , SOCK_STREAM , 0);
	if ( socket_desc == -1 )
	{
		std::cout << "Error: Could not create socket.\n";
        return;
	}

    // Attempt a connection to a local server
	if ( connect(socket_desc , (struct sockaddr *)&server_data , sizeof(server_data)) < 0 )
	{
		std::cout << "Error: Could not connect with server\n";
		return;
	}
    size_t len = frameQueue.size();
    send(socket_desc, &len, sizeof(frameQueue.size()), 0);
    // For now exit and don't send anything, later will work towards sending a mat and then multiple in sequence.
    close(socket_desc);
}
