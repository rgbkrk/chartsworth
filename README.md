## Chartsworth

<img src="https://platform.noteable.io/assets/images/chartsworth-transparent-2c87330667262616380db0fde5fbbcb6.png" height=100 />

Chartsworth posts from **notebooks** to **slack**. This little metric monster lets you post plots, images, and anything else the slack sdk will let you post.

Read more background and workflows around scheduling in the [Notebook Reporting with Chart Monsters Post](https://platform.noteable.io/blog/chart-monsters-for-slack).

### Installation and Setup

```
pip install chartsworth
```

Set environment variable `CHARTSWORTH_TOKEN` to your Slack App. You can create a new Slack App [Create a new Slack App](https://api.slack.com/apps) and [learn more about creating a new slack app in the chartsworth post](https://platform.noteable.io/blog/chart-monsters-for-slack#set-a-chart-monster-up-as-a-slack-app).

<img src="https://platform.noteable.io/assets/images/api.slack.com_set-display-information-3adccf9876820585b8cedd02341ad75e.png" height=300 />

### Usage

```python
from chartsworth import Chartsworth
chartsworth = Chartsworth("#chartsy")

new_users = 11_003
chartsworth.post(f"We have {new_users} new users")
```

Note: many times you'll need to use a channel ID (e.g. `C05HP8Z5ZPD`), especially if the channel is private. Otherwise, images will not post (only text will).

### Posting Plots

Chartsworth can take any PIL Image or Matplotlib Figure and post it to slack. This means you can post plots, images, and anything else you can think of.

```python
from chartsworth import Chartsworth

chartsworth = Chartsworth("C05HP8Z5ZPD")
chartsworth.post("Who's ready for a 🏞️ stream plot? 🧵")

import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-3, 3, 100)
y = np.linspace(-3, 3, 100)
X, Y = np.meshgrid(x, y)
u = -1 - X**2 + Y
v = 1 + X - Y**2
speed = np.sqrt(u*u + v*v)

## Create a figure we can pass to Chartsworth ##
fig, ax = plt.subplots()

strm = ax.streamplot(X, Y, u, v, color=speed, linewidth=2, cmap='autumn')
fig.colorbar(strm.lines)

## Post!
chartsworth.post(fig)
```

### Scheduling

Schedule your notebooks on Noteable from the notebooks UI

![](https://platform.noteable.io/assets/images/schedule-notebook-5afa67c7271d81c89287f869b50ec003.gif)

Or run it with [papermill](https://github.com/nteract/papermill) with your own custom scheduling!
