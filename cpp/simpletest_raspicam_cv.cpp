#include <ctime>
#include <iostream>
#include <raspicam/raspicam_cv.h>
#include <deque>
using namespace std; 

//g++ simpletest_raspicam_cv.cpp -o  simpletest_raspicam_cv -I/usr/local/include/ -lraspicam -lraspicam_cv -lmmal -lmmal_core -lmmal_util -lopencv_core -lopencv_highgui `pkg-config --cflags --libs opencv` -L/opt/vc/lib -lmmal

int main ( int argc,char **argv ) {
   deque<cv::Mat> que;
    time_t timer_begin,timer_end;
    raspicam::RaspiCam_Cv Camera;
    cv::Mat image;
    int nCount=100;
    //set camera params
    Camera.set( cv::CAP_PROP_FORMAT, CV_8UC1 );
    //Open camera
    cout<<"Opening Camera..."<<endl;
    if (!Camera.open()) {cerr<<"Error opening the camera"<<endl;return -1;}
    //Start capture
    cout<<"Capturing "<<nCount<<" frames ...."<<endl;
    time ( &timer_begin );
    for ( int i=0; i<nCount; i++ ) {
        Camera.grab();
        Camera.retrieve ( image);
        que.push_back(image);
        if ( i%5==0 )  cout<<"\r captured "<<i<<" images"<<std::flush;
    }
    cout<<"Stop camera..."<<endl;
    Camera.release();
    //show time statistics
    time ( &timer_end ); /* get current time; same as: timer = time(NULL)  */
    double secondsElapsed = difftime ( timer_end,timer_begin );
    cout<< secondsElapsed<<" seconds for "<< nCount<<"  frames : FPS = "<<  ( float ) ( ( float ) ( nCount ) /secondsElapsed ) <<endl;
    //save image 
    cv::imwrite("raspicam_cv_image.jpg",image);
    cout<<"Image saved at raspicam_cv_image.jpg"<<endl;
    cv::VideoWriter v;
    v.open("testWrite.avi", cv::VideoWriter::fourcc('H', '2', '6', '4'), 30, cv::Size(640, 480));
    cout << "Size: " << que.size() << "\n";
    int i = 0;
    while ( !que.empty() )
    {
        //v.write(cv::Mat(que.front()));
        //cv::imwrite("test/t" + to_string(i) + ".png", que.front());
        que.pop_front();
        i++;
    }
}