# To Do List

1. Try testing the mjpeg recording format and the 'vga' reolution format  
    1. Benchmark framerate on client side and server side  
        - Client Framerate on test.py -> other_debugger.py == 10 fps, which isn't what it should be.  
        - Client Framerate on raspicam_fast_srv.py -> performing as expected, roughly 27 fps when set to 30 on server, unsure if bug in measurement but server is certainly on par with 30 fps performance.  
2. Start from scratch trying to get motion detection to work the same way that it does when sending over the network with fast_srv.py and demo_client.py  
    1. Use the code from Custom Outputs section on picamera docs: https://picamera.readthedocs.io/en/release-1.13/recipes2.html#custom-outputs to build code that runs on every frame capture  
        - Came out well, runs at 15 fps with roughly 70% CPU utilization on a single frame, can be optimized significantly  
    2. Test that and make sure it runs at decent FPS while accurately catching motion on the pi  
        1. Test basic motion detection: counting white percentage  
            - Works very well, great performance and speed  
        2. Test advanced motion detection: counting from contours  
            - Does not work well, comparable to simple contour performance, much worse speed.  
    3. Test other energy estimations  
        1. Try the basic and conditional updates and see which respond to light changes best  
            - Conditional:  
                 - Pros:  
                    Looks to have amazing characteristics for robustness to light changes (it very quickly adapts the background model to a change in light intensity), it does not seem to get spoofed by light changes that are small as well.  
                - Cons:  
                    Could potentially be too insensitive to changes.  
                    Bad with current detection code that does not use contour finding. This can be adapted though especially if I continue with my idea of writing out the contour finding and area finding code in C modules and calling that through python in 1 fell swoop.  
                - Recommendation:  
                    Save for later, possible to use this or a tweaked zipfian when you have written out a more robust section of detection code that can be used without dependencies.  
            - Basic:  
                - Pros:  
                    Similar characteristics to conditional, very fast background updating time.  
                - Cons:  
                    Same issues with conditional, could be too insensitive + needs contour finding.  
        2. Compare with zipfian  
            - Conditional vs. Zipfian  
                - Conditional is way better at adjusting to changes in light source intensity  
                - Conditional updates much faster than Zipfian so you don't have lots of time spent updating the BG model slowly  
                - Conditional could be more vulnerable to slight changes in the lighting that are temporary  
                - Zipfian would perform better with detecting something that stops in view of the camera as it would integrate that object into the scene much slower.  
                - Zipfian seems to be more sensitive and catches new scene objects better  
            - Basic vs Zipfian
                - Basic updates to changes in light much faster
                - Same benefits and problems with conditional
            - Basic vs Conditional
                - Unable to notice much of a difference    
        3. Re-Test with sunlight to attempt to recreate the conditions that were making zipfian spaz out last time and verify results.  
            - Re-Test with Sunlight revealed that all 3 variants of the algorithm are relatively sensitive to shadows coming across the camera.
            - At this junction it appears the basic algorithm is the best choice currently.
    4. Optimize And Test Performance
        1. Make sure you use np.float32 dtypes in the update step for better speed  
            - Results showed no discernable difference.
        2. Try mixing smaller resizing with only running motion detection at 5-10 fps  
            - This greatly reduced load down to 20% - 25% CPU usage.
            - Attempted to conditionally scan for motion on every 6th frame while capturing at 30 fps, worked with the same level of intensity on the CPU.
        3. Test reduced framerate with slow contour finding code  
            - At 5 FPS this added some load to the CPU but was small enough that the framerate was not impacted.
            - Improved object detection significantly as compared to naive total area code
        4. Test reduced framerate detection performance  
            - When performing detection at 5 FPS while capturing at 30 FPS from camera (and sending frames to my pc) I was able to use the basic update and contour finding code the pi was able to use roughly 20% - 25% CPU utilization throughout the entire test while being able to accurately detect a falling basketball thrown by me. Basketball is around 5 inches in diameter and entering frame approximately 4-6 feet away.
        5. Test load of naive detection vs contour detection  
            - Naive detection (detection based on area of nonzero pixels) sat at around 20% CPU load for the entire test, this test did not involve sending frames to the computer, which is why it seemed to sit around 5% lower in utilization than previous testing.
            - Contour detection sat around 22.5% utilization during the same testing conditions as the naive detection above. Notably the load spiked to 35% while there was lots of data onscreen (I held my hand close to the camera which results in lots of artifacting and more contours to search). But for the most part during steady conditions the utilization is very close to naive detection and in rough conditions it appears to be worst at 35% utilization or roughly an extra 12.5% increase in utilization.
        6. Test loads on framerate capture and sending a frame  
            - Framerate capture sits around 3.5% load on CPU when capturing at 30 FPS using mjpeg format, sending 30 FPS results in another 1.5% load to total close to 5% load.
            - Capturing at 30 FPS and sending one frame out of every 6 sits at a total load of 4.5% - 5% CPU using mjepg format.
        7. Test load of computation under no motion detection load
            - Computation Load with no motion detection added is roughly the same as using the naive detection code, around 18% - 22% CPU utilization. There was no sending of frames to my computer for visualization for this test.
        ### Takeaway
        - Expect to see roughly 5% of the CPU being used by simply reading in the frames from the pi, currently it appears that the contour based motion detection code is highly dependent on how many contours exist currently in the scene, but for the common case in detection it is only slightly more expensive to the extremely bad naive detection while having significantly better detection performance.
        - The computation of the update step should add roughly 15% load to the CPU in its current configuration, this number is to be used for the basic variant of the algorithm. The Zipfian should be better but not noticeably and the Conditional variant should be worse but not in a particularly noticeable sense.
        - Further improvements can be made, consider implementing the update step in C using branchless programming as the branching is probably the biggest slowdown to a C implementation of this kind of computation. These improvements will only likely yield around a 25-50% performance improvement which would result in something like a 3% - 7% load reduction on the CPU.
    5. Implement a circular buffer and send detected motion to a server.  
    6. Implement proper motion detection code in C and call that through python.  

## Interoperable Files
- `pi_files/raspicam_fast_srv.py` -> `sigma_delta_testing/demo_client.py`
    - Get the original and compute energy image on client 
- `pi_files/test.py` -> `client_debuggers/img_debugger.py` / `client_debuggers/other_debugger.py`
    - Get just the energy image or input image
- `pi_files/basic_motion_detection.py` -> `client_debuggers/img_debugger.py`
    - Display current energy image as generated by the pi (actual live footage of the pi)