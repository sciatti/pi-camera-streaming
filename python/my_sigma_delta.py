import cv2
from numba.np.ufunc.decorators import vectorize
import numpy as np
from collections import deque
from numpy.core.fromnumeric import shape
from scipy.ndimage import gaussian_filter
import time
import timeit

N = 3
V_min = 2
V_max = 1.7976931348623157e+308 - 1.0
m = 64
T_v = 8


time_arr = []

def numpy_gauss_blur(kernel, arr):
    """Function that applies a Guassian Blur using only Numpy"""
    #kernel = np.array([1.0,2.0,1.0]) # Here you would insert your actual kernel of any size
    arr = np.apply_along_axis(lambda x: np.convolve(x, kernel, mode='same'), 0, arr)
    arr = np.apply_along_axis(lambda x: np.convolve(x, kernel, mode='same'), 1, arr)
    return arr

def highestPowerOf2(n):
    return (n & (~(n - 1)))

def basic_sigma_delta_update(I_t, M_t, V_t):
    """A basic sigma delta background subtraction algorithm"""
    M_t = np.where(M_t < I_t, M_t + 1, M_t)
    M_t = np.where(M_t > I_t, M_t - 1, M_t)

    O_t = np.absolute(M_t - I_t)

    V_t = np.where(V_t < N * O_t, V_t + 1, V_t)
    V_t = np.where(V_t > N * O_t, V_t - 1, V_t)
    V_t = np.clip(V_t, V_min, V_max)

    E_t = np.where(O_t < V_t, 0.0, 1.0)
    
    return (E_t, M_t, V_t)

def conditional_sigma_delta_update(I_t, M_t, V_t, E_t):
    """A conditional sigma delta background subtraction algorithm"""
    M_t = np.where(M_t < I_t, M_t + (1 - E_t), M_t)
    M_t = np.where(M_t > I_t, M_t - (1 - E_t), M_t)

    O_t = np.absolute(M_t - I_t)

    V_t = np.where(V_t < N * O_t, V_t + 1, V_t)
    V_t = np.where(V_t > N * O_t, V_t - 1, V_t)
    V_t = np.clip(V_t, V_min, V_max)

    E_t = np.where(O_t < V_t, 0.0, 1.0)
    
    return (E_t, M_t, V_t)

def zipfian_sigma_delta_update(I_t, M_t, V_t, E_t, t):
    """A conditional sigma delta background subtraction algorithm"""
    pi = highestPowerOf2(t % 2**m)
    sigma = 2**m / pi

    M_t = np.where(V_t > sigma, np.where(M_t < I_t, M_t + 1, M_t), M_t)
    M_t = np.where(V_t > sigma, np.where(M_t > I_t, M_t - 1, M_t), M_t)

    O_t = np.absolute(M_t - I_t)

    if (t % T_v == 0):
        V_t = np.where(V_t < N * O_t, V_t + 1, V_t)
        V_t = np.where(V_t > N * O_t, V_t - 1, V_t)
        V_t = np.clip(V_t, V_min, V_max)

    E_t = np.where(O_t < V_t, 0.0, 1.0)
    
    return (E_t, M_t, V_t)

def basic_sigma_delta_driver():
    I = deque()
    M_t, V_t = None, None
    video = cv2.VideoCapture('ball.mp4')
    #while video array is not empty:
    while True:
        ret, frame = video.read()
        if not ret:
            break
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Recevied new frame, call update step
        #I.append(frame)
        start = time.perf_counter()
        I.append(cv2.resize(frame, (frame.shape[1] // 5, frame.shape[0] // 5)))
        # First iteration book keeping
        if M_t is None:
            M_t = np.ndarray.astype(gaussian_filter(I[-1], 1), np.float64)
            V_t = np.zeros(M_t.shape, dtype=np.float64)
        
        
        E_t, M_t, V_t = basic_sigma_delta_update(I[-1], M_t, V_t)
        diff = time.perf_counter() - start
        #print("single frame exeuction time: ", diff)
        time_arr.append(diff)


        cv2.imshow('motion', cv2.resize(E_t, (E_t.shape[1] * 5, E_t.shape[0] * 5)))
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
    video.release()
    cv2.destroyAllWindows()

    print("average frame processing time: ", np.average(np.array(time_arr)))

def conditional_sigma_delta_driver():
    I = deque()
    M_t, V_t, E_t = None, None, None
    video = cv2.VideoCapture('ball.mp4')
    #while video array is not empty:
    while True:
        ret, frame = video.read()
        if not ret:
            break
        # Recevied new frame, call update step
        start = time.perf_counter()
        I.append(cv2.resize(frame, (frame.shape[1] // 5, frame.shape[0] // 5)))
        # First iteration book keeping
        if M_t is None:
            M_t = np.ndarray.astype(gaussian_filter(I[-1], 1), np.float64)
            V_t = np.zeros(M_t.shape, dtype=np.float64)
            E_t = np.zeros(M_t.shape, dtype=np.float64)
        
        E_t, M_t, V_t = conditional_sigma_delta_update(I[-1], M_t, V_t, E_t)
        diff = time.perf_counter() - start
        #print("single frame exeuction time: ", diff)
        time_arr.append(diff)


        cv2.imshow('motion', cv2.resize(E_t, (E_t.shape[1] * 5, E_t.shape[0] * 5)))
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
    video.release()
    cv2.destroyAllWindows()

    print("average frame processing time: ", np.average(np.array(time_arr)))

def zipfian_sigma_delta_driver():
    I = deque()
    M_t, V_t, E_t = None, None, None
    video = cv2.VideoCapture('ball.mp4')
    #while video array is not empty:
    while True:
        ret, frame = video.read()
        if not ret:
            break
        # Recevied new frame, call update step
        start = time.perf_counter()
        I.append(cv2.resize(frame, (frame.shape[1] // 5, frame.shape[0] // 5)))
        # First iteration book keeping
        if M_t is None:
            M_t = np.ndarray.astype(gaussian_filter(I[-1], 1), np.float64)
            V_t = np.zeros(M_t.shape, dtype=np.float64)
            E_t = np.zeros(M_t.shape, dtype=np.float64)
        
        E_t, M_t, V_t = zipfian_sigma_delta_update(I[-1], M_t, V_t, E_t, len(I))
        diff = time.perf_counter() - start
        #print("single frame exeuction time: ", diff)
        time_arr.append(diff)


        cv2.imshow('motion', cv2.resize(E_t, (E_t.shape[1] * 5, E_t.shape[0] * 5)))
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
    video.release()
    cv2.destroyAllWindows()

    print("average frame processing time: ", np.average(np.array(time_arr)))

def test_blur():
    img = cv2.imread("hubble_galaxies.jpg")
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Test different kernels and std
    scipyHalf = gaussian_filter(img, 0.5)
    scipy1 = gaussian_filter(img, 1)
    scipy2 = gaussian_filter(img, 2)
    scipy3 = gaussian_filter(img, 3)
    scipy4 = gaussian_filter(img, 4)
    scipy5 = gaussian_filter(img, 5)
    
    cv_half = cv2.GaussianBlur(img, (11, 11), 0.5)
    cv_1 = cv2.GaussianBlur(img, (11, 11), 1)
    cv_2 = cv2.GaussianBlur(img, (11, 11), 1)
    cv_3 = cv2.GaussianBlur(img, (11, 11), 1)
    cv_4 = cv2.GaussianBlur(img, (11, 11), 1)
    cv_5 = cv2.GaussianBlur(img, (11, 11), 1)
    
    cv2.imwrite("hubble_galaxies_scipy0.5.png", scipyHalf)
    cv2.imwrite("hubble_galaxies_scipy1.png", scipy1)
    cv2.imwrite("hubble_galaxies_scipy2.png", scipy2)
    cv2.imwrite("hubble_galaxies_scipy3.png", scipy3)
    cv2.imwrite("hubble_galaxies_scipy4.png", scipy4)
    cv2.imwrite("hubble_galaxies_scipy5.png", scipy5)

    cv2.imwrite("hubble_galaxies_cv_0.5.png", cv_half)
    cv2.imwrite("hubble_galaxies_cv_1.png", cv_1)
    cv2.imwrite("hubble_galaxies_cv_2.png", cv_2)
    cv2.imwrite("hubble_galaxies_cv_3.png", cv_3)
    cv2.imwrite("hubble_galaxies_cv_4.png", cv_4)
    cv2.imwrite("hubble_galaxies_cv_5.png", cv_5)


    mynumpy = numpy_gauss_blur(np.array([1.0,2.0,1.0]), img)
    cv2.imwrite("my_hubble.png", mynumpy)

if __name__ == "__main__":
    #print("time to run basic: ", timeit.timeit("basic_sigma_delta_driver()", 'from __main__ import basic_sigma_delta_driver', number=1))
    #print("time to run conditional: ", timeit.timeit("conditional_sigma_delta_driver()", 'from __main__ import conditional_sigma_delta_driver', number=1))
    basic_sigma_delta_driver()
    conditional_sigma_delta_driver()
    zipfian_sigma_delta_driver()