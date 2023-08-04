import os
from io import IOBase
from typing import Optional

from slack_sdk import WebClient


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

    def __begin_thread(self, text: str, channel: Optional[str] = None) -> str:
        """Creates a new thread (abandoning the previous one)."""
        channel = self.__determine_channel(channel)
        message_response = self.slack_client.chat_postMessage(channel=channel, text=text)

        if not message_response["ok"]:
            raise ValueError(
                f"Could not create thread for channel {channel}: {message_response}"  # noqa
            )

        thread_ts: str = message_response["ts"]  # type: ignore

        self.threads[channel] = thread_ts
        return thread_ts

    def post(self, text, channel: Optional[str] = None, **kwargs):
        """Posts a message to a thread."""
        channel = self.__determine_channel(channel)
        thread_ts = self.threads.get(channel, None)
        if thread_ts is None:
            self.__begin_thread(text, channel=channel)
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

    def post_image(self, image_stream: IOBase, filename, channel: Optional[str] = None):
        """Posts an image to a thread."""
        channel = self.__determine_channel(channel)
        thread_ts = self.threads.get(channel, None)
        if thread_ts is None:
            thread_ts = self.__begin_thread("Image :thread:", channel=channel)

        self.slack_client.files_upload(
            channel=channel,
            thread_ts=thread_ts,
            file=image_stream,
            filename=filename,
        )

    def post_monster(self):
        """Creates a monster plot and posts it to a thread."""
        channel = self.__determine_channel()
        thread_ts = self.threads.get(channel, None)
        if thread_ts is None:
            thread_ts = self.__begin_thread("Monster Plot :thread:", channel=channel)

        from .plot import create_monster_plot

        image_stream = create_monster_plot()
        self.slack_client.files_upload_v2(
            channel=channel,
            thread_ts=thread_ts,
            file=image_stream,
            filename="plot.png",
        )

    def post_figure(self, figure, channel: Optional[str] = None):
        """Posts a figure to a thread."""
        channel = self.__determine_channel(channel)
        thread_ts = self.threads.get(channel, None)
        if thread_ts is None:
            thread_ts = self.__begin_thread("Figure :thread:", channel=channel)

        from .plot import fig_to_bytes

        image_data = fig_to_bytes(figure)
        print(image_data[0])

        self.slack_client.files_upload_v2(
            channel=channel, thread_ts=thread_ts, filename="plot.png", file=image_data
        )

    def get_current_notebook_id(self):
        return os.environ["NTBL_FILE_ID"]

    def get_current_notebook_link(self):
        return f"https://{self.base_deployment}/f/{self.get_current_notebook_id()}"
