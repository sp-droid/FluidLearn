# Standard
from typing import Tuple, Any

# Third-party
import numpy as np
from numba import jit


# Colors
def srgb_to_linear(
        rgb: np.ndarray
    ) -> np.ndarray:
    """Convert sRGB color to linear RGB
    
    Args:
        rgb (np.ndarray): sRGB color values (0-1)

    Returns:
        np.ndarray: Linear RGB color values (0-1)
    """

    rgb = np.asarray(rgb, dtype=np.float32)
    return np.where(
        rgb <= 0.04045,
        rgb / 12.92,
        ((rgb + 0.055) / 1.055) ** 2.4
    )

# Arrays
@jit
def most_repeated(
        arr: np.ndarray
    ) -> Tuple[Any, int]:
    """Find most repeated element in an array

    Args:
        arr (np.ndarray): Input array

    Returns:
        any: Most repeated element
        int: Count of the most repeated element
    """

    sorted_arr = np.sort(arr)
    max_count = 1
    current_count = 1
    element = sorted_arr[0]
    for i in range(1, len(sorted_arr)):
        if sorted_arr[i] == sorted_arr[i-1]:
            current_count += 1
            if current_count > max_count:
                element = sorted_arr[i]
                max_count = current_count
        else:
            current_count = 1
    
    return element, max_count