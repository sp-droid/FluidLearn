import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import axes_grid1

def interactive_side_by_side(
        left_plot,
        right_plot,
        figsize=(10, 5),
        title_left="",
        title_right="",
        title_overall="",
        cbar_title_left=None,
        cbar_title_right=None
    ):
    """
    #### Example for contourf plots
    grid_x, grid_y = np.meshgrid(
        np.linspace(0, width, width),
        np.linspace(0, height, height)
    )
    interactive_func = lambda Frame=0: interactive_side_by_side(
        lambda ax: ax.contourf(grid_x, grid_y, velocity[Frame], levels=100, cmap="jet"),
        lambda ax: ax.contourf(grid_x, grid_y, velocity_pred[Frame], levels=100, cmap="jet"),
        figsize=(12, 4),
        title_left="Ground truth",
        title_right=f"Prediction (MSE: {losses[Frame]:.6f})",
        title_overall=f"Case name: {case_name}. Re = {data_bycase[case_name][0][0][0].item():.2f}, t = {Frame} s",
        cbar_title_left="m/s",
        cbar_title_right="m/s"
    )
    interact(interactive_func, Frame=(0, N_case-1, 1))

    #### Example for imshow plots
    interactive_func = lambda Frame=0: interactive_side_by_side(
        lambda ax: ax.imshow(velocity[Frame], extent=(0, width, 0, height), cmap="jet"),
        lambda ax: ax.imshow(velocity_pred[Frame], extent=(0, width, 0, height), cmap="jet"),
        figsize=(12, 4),
        title_left="Ground truth",
        title_right=f"Prediction (MSE: {losses[Frame]:.6f})",
        title_overall=f"Case name: {case_name}. Re = {data_bycase[case_name][0][0][0].item():.2f}, t = {Frame} s",
        cbar_title_left="m/s",
        cbar_title_right="m/s"
    )
    interact(interactive_func, Frame=(0, N_case-1, 1))
    """
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    plt.suptitle(title_overall, fontsize=12)
    # Ground truth
    ax = axes[0]
    im = left_plot(ax)
    if cbar_title_left is not None:
        cbar = add_cbar(im, ax)
        cbar.ax.set_title(cbar_title_left)
    ax.set_title(title_left)

    # Prediction
    ax = axes[1]
    im = right_plot(ax)
    if cbar_title_right is not None:
        cbar = add_cbar(im, ax)
        cbar.ax.set_title(cbar_title_right)
    ax.set_title(title_right)

    plt.tight_layout()
    plt.show()

def add_cbar(im, ax, aspect=20, pad_fraction=0.5, **kwargs):
    """Add a vertical color bar to an image plot."""
    divider = axes_grid1.make_axes_locatable(im.axes)
    width = axes_grid1.axes_size.AxesY(im.axes, aspect=1./aspect)
    pad = axes_grid1.axes_size.Fraction(pad_fraction, width)
    cax = divider.append_axes("right", size=width, pad=pad)
    plt.sca(ax)
    return im.axes.figure.colorbar(im, cax=cax, **kwargs)