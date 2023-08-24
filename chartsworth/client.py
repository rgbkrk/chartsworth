import io
import os
from typing import Optional, Union

import matplotlib.pyplot as plt
import PIL.Image
from matplotlib.figure import Figure
from slack_sdk import WebClient

from .plot import create_monster_plot


class Chartsworth:
    """Chartsworth is a Chart Monster for posting from notebooks to Slack.

    Chartsworth loves threads. Every new instance of chartsworth will try to
    reuse existing threads per channel."""

    def __init__(self, default_channel=None, base_deployment=None):
        # Set up Chartsworth
        slack_token = os.getenv("CHARTSWORTH_SLACK_TOKEN", None)
        if slack_token is None:
            raise ValueError("CHARTSWORTH_SLACK_TOKEN not set as an environment variable")

        self.base_deployment = base_deployment
        if self.base_deployment is None:
            self.base_deployment = "app.noteable.io"

        self.slack_client = WebClient(token=slack_token)
        self.default_channel = default_channel
        self.threads = {}

    def __determine_channel(self, channel: Optional[str] = None) -> str:
        if channel is not None:
            return channel

        channel = self.default_channel
        if channel is None:
            raise ValueError(
                "No default channel set. "
                "Pass a channel in or set a default channel when initializing"
            )
        return channel

    def __begin_thread(self, text: str, channel: Optional[str] = None, **kwargs) -> str:
        """Creates a new thread (abandoning the previous one)."""
        channel = self.__determine_channel(channel)
        message_response = self.slack_client.chat_postMessage(channel=channel, text=text, **kwargs)

        if not message_response["ok"]:
            raise ValueError(
                f"Could not create thread for channel {channel}: {message_response}"  # noqa
            )

        thread_ts: str = message_response["ts"]  # type: ignore

        self.threads[channel] = thread_ts
        return thread_ts

    def post(
        self,
        any: Union[str, io.IOBase, PIL.Image.Image, Figure],
        channel: Optional[str] = None,
        **kwargs,
    ):
        """Posts a message or image to a thread."""
        if isinstance(any, str):
            self.post_text(any, channel=channel, **kwargs)
        else:
            self.post_image(any, channel=channel, **kwargs)

    def post_text(self, text: str, channel: Optional[str] = None, **kwargs):
        """Posts a message to a thread."""
        channel = self.__determine_channel(channel)
        thread_ts = self.threads.get(channel, None)
        if thread_ts is None:
            self.__begin_thread(text, channel=channel, **kwargs)
            return

        self.slack_client.chat_postMessage(
            channel=channel, thread_ts=thread_ts, text=text, **kwargs
        )

    def react_to_thread(self, name, channel: Optional[str] = None):
        channel = self.__determine_channel(channel)
        thread_ts = self.threads.get(channel, None)
        if thread_ts is None:
            thread_ts = self.__begin_thread("Post :thread:", channel=channel)

        self.slack_client.reactions_add(channel=channel, timestamp=thread_ts, name=name)

    def post_image(
        self,
        image: Union[io.BytesIO, PIL.Image.Image, Figure],
        filename: str,
        channel: Optional[str] = None,
    ):
        """Posts an image to a thread."""
        channel = self.__determine_channel(channel)
        thread_ts = self.threads.get(channel, None)
        if thread_ts is None:
            thread_ts = self.__begin_thread("Image :thread:", channel=channel)

        image_stream = io.BytesIO()

        if isinstance(image, PIL.Image.Image):
            image.save(image_stream, format="PNG")
        elif isinstance(image, Figure):
            plt.close(image)
            image.savefig(image_stream, format="PNG")
        else:
            image_stream = image

        if filename is None:
            filename = "image.png"
        filename = filename[:160]
        if not filename.endswith(".png"):
            filename += ".png"

        image_stream.seek(0)

        try:
            self.slack_client.files_upload_v2(
                channel=channel,
                thread_ts=thread_ts,
                file=image_stream,
                filename=filename,
            )
        except Exception:
            import traceback

            from IPython.core.display_functions import display

            self.post(
                f"Unable to upload `{filename}` to Slack. Check the <{self.notebook_link}|Notebook> for more details."
            )
            display(
                {
                    "text/markdown": "Sometimes slack will fail to upload images, especially if using a Channel Name rather than an ID."
                },
                raw=True,
            )

            traceback_str = traceback.format_exc()
            print(traceback_str)

    def post_monster(self, text: str, channel: Optional[str] = None):
        """Creates a monster plot and posts it to a thread."""
        channel = self.__determine_channel(channel)
        thread_ts = self.threads.get(channel, None)
        if thread_ts is None:
            thread_ts = self.__begin_thread("Monster Plot :thread:", channel=channel)

        figure = create_monster_plot()

        self.post_image(figure, "monster_plot.png", channel=channel)

    def get_current_notebook_id(self):
        return os.environ.get("NTBL_FILE_ID", None)

    def get_current_notebook_link(self):
        return f"https://{self.base_deployment}/f/{self.get_current_notebook_id()}"

    @property
    def notebook_link(self):
        return self.get_current_notebook_link()

    @property
    def notebook_id(self):
        return self.get_current_notebook_id()
