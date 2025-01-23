"""
Convenience math functions.

Author(s): Derek Fan
"""

from ulab import numpy as np


def skew(v: np.ndarray):
    return np.array(
        [
            [0.0, -v[2], v[1]],
            [v[2], 0.0, -v[0]],
            [-v[1], v[0], 0.0],
        ]
    )


def is_near(a: float, b: float, tol=1e-6) -> bool:
    return abs(a - b) < tol

def quat_to_R(q : np.ndarray) -> np.ndarray:
    """
        Converts a quaternion [w, x, y, z] into its 3x3 rotation matrix
    """
    q0 = q[0]
    q1 = q[1]
    q2 = q[2]
    q3 = q[3]
     
    # First row of the rotation matrix
    r00 = 2 * (q0 * q0 + q1 * q1) - 1
    r01 = 2 * (q1 * q2 - q0 * q3)
    r02 = 2 * (q1 * q3 + q0 * q2)
     
    # Second row of the rotation matrix
    r10 = 2 * (q1 * q2 + q0 * q3)
    r11 = 2 * (q0 * q0 + q2 * q2) - 1
    r12 = 2 * (q2 * q3 - q0 * q1)
     
    # Third row of the rotation matrix
    r20 = 2 * (q1 * q3 - q0 * q2)
    r21 = 2 * (q2 * q3 + q0 * q1)
    r22 = 2 * (q0 * q0 + q3 * q3) - 1
     
    # 3x3 rotation matrix
    rot_matrix = np.array([[r00, r01, r02],
                           [r10, r11, r12],
                           [r20, r21, r22]])
                            
    return rot_matrix

def R_to_quat(R : np.ndarray) -> np.ndarray:
    """
        Converts a 3x3 rotation matrix into its quaternion representation
    """
    # TODO : assertions to ensure R is a 3x3 matrix
    
    w = np.sqrt(1.0 + R[0,0] + R[1,1] + R[2,2]) / 2.0
    w4 = (4.0 * w)
 
    x = (R[2,1] - R[1,2]) / w4
    y = (R[0,2] - R[2,0]) / w4
    z = (R[1,0] - R[0,1]) / w4
    
    return np.array([w, x, y, z])

def rotvec_to_R(vec : np.ndarray) -> np.ndarray:
    """
        Converts an axis-angle vector into its 3x3 rotation matrix
    """
    theta = np.linalg.norm(vec)
    ct = np.cos(theta)
    st = np.sin(theta)
    
    unit_vec = vec/theta
    vx = unit_vec[0]
    vy = unit_vec[1]
    vz = unit_vec[2]
    
    
    R = np.array([[ct + vx**2*(1-ct), vx*vy*(1-ct) - vz*st, vx*vz*(1-ct) + vy*st],
                  [vx*vy*(1-ct)+ vz*st, ct + vy**2*(1-ct), vy*vz*(1-ct) - vz*st],
                  [vz*vx*(1-ct) - vy*st, vz*vy*(1-ct) + vx*st, ct + vz**2*(1-ct)]])
    
    return R