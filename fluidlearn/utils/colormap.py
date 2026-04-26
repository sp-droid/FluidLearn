# Standard
from typing import Literal, Callable

# Third-party
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

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

class Colormap:
    _available_cmaps = ["jet", "binary", "random", "hsv", "viridis", "plasma", "inferno", "magma", "cividis", "turbo", "coolwarm", "RdBu", "twilight","terrain"]
    def __init__(self):
        pass

    @property
    def available_cmaps(self):
        return self._available_cmaps

    def set_cmap(self, cmap_name: str, reverse: bool=False):
        self._name = cmap_name
        if reverse: self._name += "_r"
        self._function = plt.colormaps[self._name]
    @property
    def name(self): return self._name

    def __call__(self, array):
        return self._function(array)

    def build_lut(
            self,
            N_colors: int=256,
            logscale: bool=False,
            space: Literal["sRGB", "linear"] = "sRGB"
        ):
        """Build a lookup table for the colormap with N_colors entries. In sRGB space, so values are in [0, 1]
        
        """
        
        if logscale:
            self._lut = np.array([self(np.log10(i)/(np.log10(N_colors))) for i in range(1, N_colors+1)]).astype(np.float32)
        else:
            self._lut = np.array([self(i/(N_colors-1)) for i in range(N_colors)]).astype(np.float32)
        
        match space:
            case "linear":
                self._lut[:, :3] = srgb_to_linear(self._lut[:, :3])
    @property
    def lut(self): return self._lut