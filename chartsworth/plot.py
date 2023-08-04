import io

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg


def create_monster_plot():
    """Creates a monster plot and returns a BytesIO object with the plot.

    Mostly for testing but also for fun."""
    # Create a BytesIO object.
    # This is where we'll store the plot for Slack.
    image_stream = io.BytesIO()

    # Create some eyes
    eye1_x = np.random.uniform(0.25, 0.75)
    eye1_y = np.random.uniform(0.7, 0.9)
    eye2_x = np.random.uniform(0.25, 0.75)
    eye2_y = np.random.uniform(0.7, 0.9)
    plt.plot(eye1_x, eye1_y, "o", markersize=20, color="black")
    plt.plot(eye2_x, eye2_y, "o", markersize=20, color="black")

    # Create a mouth
    x = np.linspace(0, 1, 100)
    y = 0.2 + 0.1 * np.sin(
        np.random.uniform(1, 10) * x + np.random.uniform(0, 2 * np.pi)
    )
    plt.plot(x, y, color="black", linewidth=2)

    # Set the aspect ratio of the plot to 1 so the monster looks dope
    plt.gca().set_aspect("equal", adjustable="box")
    # plt.axis('off')
    plt.ylim(0, 1)

    # Save the figure to the BytesIO object
    plt.savefig(image_stream, format="png")

    # Return an image stream at the start
    image_stream.seek(0)
    return image_stream


def fig_to_bytes(fig):
    """Converts a matplotlib figure to a BytesIO object."""
    canvas = FigureCanvasAgg(fig)
    canvas.draw()

    image_bytes = canvas.tostring_rgb()
    return image_bytes
