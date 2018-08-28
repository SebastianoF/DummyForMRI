import numpy as np


# ---------- Dummy building blocks ---------------


def sphere_shape(omega, centre, radius, foreground_intensity=100, dtype=np.uint8):
    sky = np.zeros(omega, dtype=dtype)
    for xi in range(omega[0]):
        for yi in range(omega[1]):
            for zi in range(omega[2]):
                if np.sqrt((centre[0] - xi) ** 2 + (centre[1] - yi) ** 2 + (centre[2] - zi) ** 2) <= radius:
                    sky[xi, yi, zi] = foreground_intensity
    return sky


def ellipsoid_shape(omega, focus_1, focus_2, distance, background_intensity=0, foreground_intensity=100,
                    dtype=np.uint8):
    sky = background_intensity * np.ones(omega, dtype=dtype)
    for xi in range(omega[0]):
        for yi in range(omega[1]):
            for zi in range(omega[2]):
                if np.sqrt((focus_1[0] - xi) ** 2 + (focus_1[1] - yi) ** 2 + (focus_1[2] - zi) ** 2) + \
                        np.sqrt((focus_2[0] - xi) ** 2 + (focus_2[1] - yi) ** 2 + (focus_2[2] - zi) ** 2) <= distance:
                    sky[xi, yi, zi] = foreground_intensity
    return sky


def oval_shape(omega, centre, foreground_intensity=1, alpha=(0.18,0.18), dd=None, a_b_c=None, dtype=np.uint8):
    """
    From the ellipsoid equation in canonic form.
    Pebble-like stone shape with a principal direction. Can represent a biological shape phantom.

    :param omega:
    :param centre:
    :param foreground_intensity:
    :param alpha: between 0.1 and 0.3 maximal range
    :param dd: maximal extension, smaller than 2 * np.sqrt(omega[direction])
    :return:
    """
    sky = np.zeros(omega, dtype=dtype)

    if a_b_c is None:
        a_b_c = [1, 2, 1]
    if dd is None:
        dd = 2 * np.sqrt(omega[1])
    a_b_c = dd * np.array(a_b_c)
    for xi in range(omega[0]):
        for yi in range(omega[1]):
            for zi in range(omega[2]):
                if (np.abs(xi - centre[0]) / float(a_b_c[0])) ** 2 * (1 + alpha[0] * zi) / dd + (np.abs(yi - centre[1]) / float(a_b_c[1])) ** 2 + (np.abs(zi - centre[2]) / float(a_b_c[2])) ** 2 * (1 + alpha[1] * yi) / dd < 1:
                    sky[xi, yi, zi] = foreground_intensity

    return sky


def sulci_structure(omega, centre, foreground_intensity=1, a_b_c=None, dd=None, random_perturbation=0,
                    alpha=(0.18,0.18), dtype=np.uint8):
    sky = np.zeros(omega, dtype=dtype)

    if a_b_c is None:
        a_b_c = [1, 2, 1]
    if dd is None:
        dd = 2 * np.sqrt(omega[1])
    a_b_c = dd * np.array(a_b_c)

    thetas = [j * np.pi / 4 for j in range(0, 8)]
    phis = [j * np.pi / 4 for j in range(1,4)]

    radius_internal_foci = a_b_c[0]
    radius_external_foci = a_b_c[1]

    internal_foci = []
    external_foci = []

    for theta in thetas:
        for phi in phis:
            p = np.array([np.cos(theta) * np.sin(phi), np.sin(theta) * np.sin(phi), np.cos(phi)])
            # deform according to ovoidal shape
            A, B, C, D = np.sum([(p[j]/float(a_b_c[j])) ** 2 for j in range(3)]), (p[0]/float(a_b_c[0])) ** 2 * alpha[0] * p[2] + (p[2]/float(a_b_c[2])) ** 2 * alpha[1] * p[1], 0, -1
            t = [np.real(j) for j in np.roots([A, B, C, D]) if np.abs(np.imag(j)) < 10e-6][0]
            internal_foci.append((radius_internal_foci + t) * p + np.array(centre))
            external_foci.append((radius_external_foci + t) * p + np.array(centre))

    # add north and south pole:
    internal_foci.append(radius_internal_foci * np.array([0, 0, 1]) + np.array(centre))
    internal_foci.append(radius_internal_foci * np.array([0, 0, -1]) + np.array(centre))

    external_foci.append(radius_external_foci * np.array([0, 0, 1]) + np.array(centre))
    external_foci.append(radius_external_foci * np.array([0, 0, -1]) + np.array(centre))

    # generate ellipses:
    for inte, exte in zip(internal_foci, external_foci):
        d = 1.3 * np.linalg.norm(inte - exte)
        if random_perturbation > 0:
            random_perturbation = 0.1* random_perturbation
            epsilon_radius = random_perturbation * np.random.randn() * d
            epsilon_direction = np.linalg.norm(inte - exte) * 0.5 * random_perturbation * np.random.randn(3)
            sky += ellipsoid_shape(omega, inte, exte + epsilon_direction, d + epsilon_radius, background_intensity=0, foreground_intensity=foreground_intensity)
        else:
            sky += ellipsoid_shape(omega, inte, exte, d, background_intensity=0, foreground_intensity=foreground_intensity)

    return sky
