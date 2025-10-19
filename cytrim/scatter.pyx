# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
"""Treat the scattering of a projectile on a target atom (Cython optimized).

Currently, only the ZBL potential (Ziegler, Biersack, Littmark,
The Stopping and Range of Ions in Matter, Pergamon Press, 1985) is 
implemented, along with Biersack's "magic formula" for the scattering 
angle.

Available functions:
    setup: setup module variables.
    scatter: treat a scattering event.
"""
from libc.math cimport sqrt, exp
import numpy as np
cimport numpy as cnp

cnp.import_array()

# Module-level variables
cdef double ENORM
cdef double RNORM
cdef double DIRFAC
cdef double DENFAC

# Constants for ZBL screening function
cdef double A1 = 0.18175
cdef double A2 = 0.50986
cdef double A3 = 0.28022
cdef double A4 = 0.02817

cdef double B1 = 3.1998
cdef double B2 = 0.94229
cdef double B3 = 0.4029
cdef double B4 = 0.20162

cdef double A1B1 = A1 * B1
cdef double A2B2 = A2 * B2
cdef double A3B3 = A3 * B3
cdef double A4B4 = A4 * B4

# Constants for apsis estimation
cdef double K2 = 0.38
cdef double K3 = 7.2
cdef double K1 = 1.0/(4.0*K2)
cdef double R12sq = (2.0*K2)*(2.0*K2)
cdef double R23sq = K3 / K2
cdef int NITER = 1

# Constants for magic formula
cdef double C1 = 0.99229
cdef double C2 = 0.011615
cdef double C3 = 0.007122
cdef double C4 = 14.813
cdef double C5 = 9.3066


def setup(int z1, double m1, int z2, double m2):
    """Setup module variables depending on projectile and target species.

    Parameters:
        z1 (int): atomic number of projectile
        m1 (float): mass of projectile (amu)
        z2 (int): atomic number of target
        m2 (float): mass of target (amu)

    Returns:
        None    
    """
    global ENORM, RNORM, DIRFAC, DENFAC

    cdef double m1_m2 = m1 / m2
    cdef double z1_023 = z1**0.23
    cdef double z2_023 = z2**0.23
    
    RNORM = 0.4685 / (z1_023 + z2_023)
    ENORM = 14.39979 * z1 * z2 / RNORM * (1.0 + m1_m2)
    DIRFAC = 2.0 / (1.0 + m1_m2)
    DENFAC = 4.0 * m1_m2 / ((1.0 + m1_m2)*(1.0 + m1_m2))


cdef inline void ZBLscreen(double r, double* screen, double* dscreen) nogil:
    """Calculate the ZBL screening function and its derivative.

    Parameters:
        r (double): Distance (RNORM)
        screen (double*): Output - ZBL potential at distance r (ENORM)
        dscreen (double*): Output - derivative of ZBL potential (ENORM/RNORM)
    """
    cdef double exp1 = exp(-B1 * r)
    cdef double exp2 = exp(-B2 * r)
    cdef double exp3 = exp(-B3 * r)
    cdef double exp4 = exp(-B4 * r)
    
    screen[0] = A1*exp1 + A2*exp2 + A3*exp3 + A4*exp4
    dscreen[0] = -(A1B1*exp1 + A2B2*exp2 + A3B3*exp3 + A4B4*exp4)


cdef inline double estimate_apsis(double e, double p) nogil:
    """Estimate the distance of closest approach (apsis) in a collision.

    Parameters:
        e (double): energy of projectile before the collision (ENORM)
        p (double): impact parameter (RNORM)

    Returns:
        double: Estimated apsis of the collision (RNORM)
    """
    cdef double psq = p * p
    cdef double r0sq = 0.5 * (psq + sqrt(psq*psq + 4.0*K3/e))
    cdef double r0
    cdef double screen, dscreen
    cdef double numerator, denominator, residuum
    cdef int i

    if r0sq < R23sq:
        r0sq = psq + K2/e
        if r0sq < R12sq:
            r0 = (1.0 + sqrt(1.0 + 4.0*e*(e+K1)*psq)) / (2.0*(e+K1))
        else:
            r0 = sqrt(r0sq)
    else:
        r0 = sqrt(r0sq)
    
    # Newton-Raphson iterations
    for i in range(NITER):
        ZBLscreen(r0, &screen, &dscreen)
        numerator = r0*(r0-screen/e) - psq
        denominator = 2.0*r0 - (screen+r0*dscreen)/e
        r0 -= numerator/denominator

        residuum = 1.0 - screen/(e*r0) - psq/(r0*r0)
        if residuum < 1e-4 and residuum > -1e-4:
            break

    return r0


cdef inline double magic(double e, double p) nogil:
    """Calculate CM scattering angle using Biersack's magic formula.

    Parameters:
        e (double): energy of projectile before the collision (ENORM)
        p (double): impact parameter (RNORM)
    
    Returns:
        double: cosine of half the scattering angle in the center-of-mass system
    """
    cdef double r0 = estimate_apsis(e, p)
    cdef double screen, dscreen
    cdef double rho, sqrte, alpha, beta, gamma, a, g, delta
    cdef double cos_half_theta
    
    ZBLscreen(r0, &screen, &dscreen)

    rho = 2.0*(e*r0-screen) / (screen/r0-dscreen)
    sqrte = sqrt(e)
    alpha = 1.0 + C1/sqrte
    beta = (C2+sqrte) / (C3+sqrte)
    gamma = (C4+e) / (C5+e)
    a = 2.0 * alpha * e * (p**beta)
    g = gamma / (sqrt(1.0+a*a)-a)
    delta = a * (r0-p) / (1.0+g)

    cos_half_theta = (p + rho + delta) / (r0 + rho)
    
    return cos_half_theta


cpdef tuple scatter(double e, cnp.ndarray[cnp.float64_t, ndim=1] dir, 
                     double p, cnp.ndarray[cnp.float64_t, ndim=1] dirp):
    """Treat a scattering event.

    The atomic numbers and masses of the projectile and target enter the
    calculation via the module variables ENORM, PNORM, DIRFAC, and DENFAC.

    The direction vectors dir and dirp are assumed to be normalized to 
    unit length.

    Parameters:
        e (float): energy of the projectile before the collision (eV)
        dir (ndarray): direction vector of the projectile before 
            the collision (size 3)
        p (float): impact parameter (A)
        dirp (ndarray): direction vector of the impact parameter
            (= from the collision point to the recoil position before 
            the collision) (size 3)
    
    Returns:
        tuple: (dir_new, e_new, dir_recoil, e_recoil)
    """
    cdef double cos_half_theta = magic(e/ENORM, p/RNORM)
    cdef double sin_psi = cos_half_theta
    cdef double cos_psi = sqrt(1.0 - sin_psi*sin_psi)
    cdef double norm
    cdef double e_recoil
    cdef cnp.ndarray[cnp.float64_t, ndim=1] dir_recoil = np.empty(3, dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] dir_new = np.empty(3, dtype=np.float64)
    cdef int i

    # Calculate recoil direction
    for i in range(3):
        dir_recoil[i] = DIRFAC * cos_psi * (cos_psi*dir[i] + sin_psi*dirp[i])
    
    # Calculate new projectile direction
    for i in range(3):
        dir_new[i] = dir[i] - dir_recoil[i]
    
    # Normalize dir_new
    norm = sqrt(dir_new[0]*dir_new[0] + dir_new[1]*dir_new[1] + dir_new[2]*dir_new[2])
    if norm == 0:
        for i in range(3):
            dir_new[i] = dir[i]
    else:
        for i in range(3):
            dir_new[i] /= norm
    
    # Normalize dir_recoil
    norm = sqrt(dir_recoil[0]*dir_recoil[0] + dir_recoil[1]*dir_recoil[1] + 
                dir_recoil[2]*dir_recoil[2])
    if norm == 0:
        for i in range(3):
            dir_recoil[i] = dir[i]
    else:
        for i in range(3):
            dir_recoil[i] /= norm

    # Calculate energy after scattering
    e_recoil = DENFAC * e * (1.0 - cos_half_theta*cos_half_theta)
    e -= e_recoil

    return (dir_new, e, dir_recoil, e_recoil)
