"""methods to calculate adjaceny"""

import numpy as np
from numba import njit, prange


@njit("f4(f4[:], f4[:])")
def euclid_dist(t1, t2):
    """compute euclidean dist"""
    sum_i = 0
    for i in range(t1.shape[0]):
        sum_i += (t1[i] - t2[i]) ** 2
    return np.sqrt(sum_i)


@njit("f4[:,:](f4[:,:])", parallel=True, nogil=True)
def pairwise_distance(X):
    """get pairwise"""
    n = X.shape[0]
    adj = np.empty((n, n), dtype=np.float32)
    for i in prange(n):
        for j in prange(n):
            adj[i][j] = euclid_dist(X[i], X[j])
    return adj


def extract_color(x_pixel=None, y_pixel=None, image=None, beta=49):
    """extract standarized color from image"""
    # beta to control the range of neighbourhood when calculate grey vale for
    # one spot
    beta_half = round(beta / 2)
    g = []
    for i, x_p in enumerate(x_pixel):
        max_x = image.shape[0]
        max_y = image.shape[1]
        y_p = y_pixel[i]
        nbs = image[
            max(0, x_p - beta_half) : min(max_x, x_p + beta_half + 1),
            max(0, y_p - beta_half) : min(max_y, y_p + beta_half + 1),
        ]
        g.append(np.mean(np.mean(nbs, axis=0), axis=0))
    c0, c1, c2 = [], [], []
    for i in g:
        c0.append(i[0])
        c1.append(i[1])
        c2.append(i[2])
    c0 = np.array(c0)
    c1 = np.array(c1)
    c2 = np.array(c2)
    c3 = (c0 * np.var(c0) + c1 * np.var(c1) + c2 * np.var(c2)) / (
        np.var(c0) + np.var(c1) + np.var(c2)
    )
    return c3


def calculate_adj_matrix(
    x,
    y,
    x_pixel=None,
    y_pixel=None,
    image=None,
    beta=49,
    alpha=1,
    histology=True,
):
    """calculate adjacency"""
    # x,y,x_pixel, y_pixel are lists
    if histology:
        assert (x_pixel is not None) & (x_pixel is not None)
        assert image is not None
        assert (len(x) == len(x_pixel)) & (len(y) == len(y_pixel))
        # print("Calculateing adj matrix using histology image...")
        # beta to control the range of neighbourhood when calculate grey vale
        # for one spot
        # alpha to control the color scale
        beta_half = round(beta / 2)
        g = []
        for i, x_p in enumerate(x_pixel):
            max_x = image.shape[0]
            max_y = image.shape[1]
            y_p = y_pixel[i]
            nbs = image[
                max(0, x_p - beta_half) : min(max_x, x_p + beta_half + 1),
                max(0, y_p - beta_half) : min(max_y, y_p + beta_half + 1),
            ]
            g.append(np.mean(np.mean(nbs, axis=0), axis=0))
        c0, c1, c2 = [], [], []
        for i in g:
            c0.append(i[0])
            c1.append(i[1])
            c2.append(i[2])
        c0 = np.array(c0)
        c1 = np.array(c1)
        c2 = np.array(c2)
        # print("Var of c0,c1,c2 = ", np.var(c0), np.var(c1), np.var(c2))
        c3 = (c0 * np.var(c0) + c1 * np.var(c1) + c2 * np.var(c2)) / (
            np.var(c0) + np.var(c1) + np.var(c2)
        )
        c4 = (c3 - np.mean(c3)) / np.std(c3)
        z_scale = np.max([np.std(x), np.std(y)]) * alpha
        z = c4 * z_scale
        z = z.tolist()
        # print("Var of x,y,z = ", np.var(x), np.var(y), np.var(z))
        _x = np.array([x, y, z]).T.astype(np.float32)
    else:
        # print("Calculateing adj matrix using xy only...")
        _x = np.array([x, y]).T.astype(np.float32)
    return pairwise_distance(_x)
