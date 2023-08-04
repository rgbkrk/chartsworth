import matplotlib.pyplot as plt
import numpy as np


def create_monster_plot():
    """Creates a monster plot and returns a Matplotlib figure object.

    Mostly for testing but also for fun."""
    # Create a Matplotlib figure object.
    fig, ax = plt.subplots()

    # Create some eyes
    eye1_x = np.random.uniform(0.25, 0.75)
    eye1_y = np.random.uniform(0.7, 0.9)
    eye2_x = np.random.uniform(0.25, 0.75)
    eye2_y = np.random.uniform(0.7, 0.9)
    ax.plot(eye1_x, eye1_y, "o", markersize=20, color="black")
    ax.plot(eye2_x, eye2_y, "o", markersize=20, color="black")

    # Create a mouth
    x = np.linspace(0, 1, 100)
    y = 0.2 + 0.1 * np.sin(np.random.uniform(1, 10) * x + np.random.uniform(0, 2 * np.pi))
    ax.plot(x, y, color="black", linewidth=2)

    # Set the aspect ratio of the plot to 1 so the monster looks dope
    ax.set_aspect("equal", adjustable="box")
    ax.set_ylim(0, 1)

    # Don't let matplotlib show the plot immediately
    plt.close(fig)

    return fig
