import numpy as np

N = 3
V_min = 2

def highestPowerOf2(n):
    return (n & (~(n - 1)))

def basic_sigma_delta_update(I_t, M_t, V_t, arrType):
    """A basic sigma delta background subtraction algorithm"""
    V_max = np.finfo(arrType).max
    M_t = np.where(M_t < I_t, M_t + 1, M_t)
    M_t = np.where(M_t > I_t, M_t - 1, M_t)

    O_t = np.absolute(M_t - I_t)

    V_t = np.where(V_t < N * O_t, V_t + 1, V_t)
    V_t = np.where(V_t > N * O_t, V_t - 1, V_t)
    V_t = np.clip(V_t, V_min, V_max)

    E_t = np.where(O_t < V_t, 0.0, 1.0)

    return (E_t, M_t, V_t)

def conditional_sigma_delta_update(I_t, M_t, V_t, E_t, arrType):
    """A conditional sigma delta background subtraction algorithm"""
    V_max = np.finfo(arrType).max
    M_t = np.where(M_t < I_t, M_t + (1 - E_t), M_t)
    M_t = np.where(M_t > I_t, M_t - (1 - E_t), M_t)

    O_t = np.absolute(M_t - I_t)

    V_t = np.where(V_t < N * O_t, V_t + 1, V_t)
    V_t = np.where(V_t > N * O_t, V_t - 1, V_t)
    V_t = np.clip(V_t, V_min, V_max)

    E_t = np.where(O_t < V_t, 0.0, 1.0)

    return (E_t, M_t, V_t)

def zipfian_sigma_delta_update(I_t, M_t, V_t, E_t, t, m, T_v, arrType):
    """A conditional sigma delta background subtraction algorithm"""
    V_max = np.finfo(arrType).max
    pi = highestPowerOf2(t % 2**m)
    sigma = 2**m / pi

    M_t = np.where(V_t > sigma, np.where(M_t < I_t, M_t + 1, M_t), M_t)
    M_t = np.where(V_t > sigma, np.where(M_t > I_t, M_t - 1, M_t), M_t)

    O_t = np.absolute(M_t - I_t)

    if t % T_v == 0:
        V_t = np.where(V_t < N * O_t, V_t + 1, V_t)
        V_t = np.where(V_t > N * O_t, V_t - 1, V_t)
        V_t = np.clip(V_t, V_min, V_max)

    E_t = np.where(O_t < V_t, 0.0, 1.0)

    return E_t, M_t, V_t
