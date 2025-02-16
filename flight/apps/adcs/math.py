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


def quat_to_R(q: np.ndarray) -> np.ndarray:
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
    rot_matrix = np.array([[r00, r01, r02], [r10, r11, r12], [r20, r21, r22]])

    return rot_matrix


def R_to_quat(R: np.ndarray) -> np.ndarray:
    """
    Converts a 3x3 rotation matrix into its quaternion representation
    """
    # TODO : assertions to ensure R is a 3x3 matrix

    w = np.sqrt(1.0 + R[0, 0] + R[1, 1] + R[2, 2]) / 2.0
    w4 = 4.0 * w

    x = (R[2, 1] - R[1, 2]) / w4
    y = (R[0, 2] - R[2, 0]) / w4
    z = (R[1, 0] - R[0, 1]) / w4

    return np.array([w, x, y, z])


def quaternion_multiply(q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
    q = np.zeros((4,))

    q[0] = q1[0] * q2[0] - q1[1] * q2[1] - q1[2] * q2[2] - q1[3] * q2[3]
    q[1] = q1[0] * q2[1] + q1[1] * q2[0] + q1[2] * q2[3] - q1[3] * q2[2]
    q[2] = q1[0] * q2[2] - q1[1] * q2[3] + q1[2] * q2[0] + q1[3] * q2[1]
    q[3] = q1[0] * q2[3] + q1[1] * q2[2] - q1[2] * q2[1] + q1[3] * q2[0]

    return q


def invert_3x3_psd(matrix):
    """
    Inverts a 3x3 symmetric matrix using the classical adjoint (cofactor) method.
    Returns a new 3x3 matrix that is the inverse of 'matrix' or none if it is not invertible.
    About twice faster than np.linalg.inv
    """
    if matrix.shape != (3, 3):
        raise ValueError("Matrix must be 3x3.")

    # Helper aliases for clarity
    a, b, c = matrix[0]
    _, e, f = matrix[1]
    _, _, i = matrix[2]

    # Calculate the determinant
    det = a * (e * i - f * f) - b * (b * i - 2 * f * c) - e * c * c

    if abs(det) < 1e-12:  # If determinant is (near) zero, it's not invertible
        return None

    # Calculate cofactors (matrix of minors with alternating signs)
    # Cofactor matrix (not yet transposed):
    adjugate = np.array(
        [
            [(e * i - f * f), -(b * i - f * c), (b * f - e * c)],
            [-(b * i - c * f), (a * i - c * c), -(a * f - b * c)],
            [(b * f - c * e), -(a * f - c * b), (a * e - b * b)],
        ]
    )

    # Multiply adjugate by 1/det to get the inverse
    inv = adjugate / det
    return inv
