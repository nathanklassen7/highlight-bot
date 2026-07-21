"""Preview clip/session handlers: compress, upload to channel, delete temp."""

import logging
import os
import threading

from consts import CLIP_DIRECTORY
from file_management.file_read_lock import file_read_lock
from file_management.get_sessions import get_session_at_index
from interactions.BlockInteraction import BlockInteraction
from preview_utils import make_clip_preview, make_session_preview
from server_utils import post_file_to_channel_or_thread

logger = logging.getLogger(__name__)


def _unlink_quiet(path: str | None):
    if path and os.path.isfile(path):
        try:
            os.unlink(path)
        except OSError as e:
            logger.error("Failed to delete preview file %s: %s", path, e)


def preview_clip(interaction: BlockInteraction):
    filename = interaction.button_value
    input_path = f"{CLIP_DIRECTORY}{filename}"

    def _run():
        output_path = None
        try:
            output_path = make_clip_preview(input_path)
            clip_id = filename.removesuffix(".mp4")[:8]
            post_file_to_channel_or_thread(
                interaction.channel_id,
                output_path,
                f"Preview: {clip_id}",
            )
        except Exception as e:
            logger.error("Clip preview failed: %s", e)
            interaction.update_with_message(f"Preview failed: {e}")
        finally:
            _unlink_quiet(output_path)
            file_read_lock.release()

    threading.Thread(target=_run, daemon=True).start()


def preview_session(interaction: BlockInteraction):
    session_index = int(interaction.button_value)
    filenames = get_session_at_index(session_index)

    def _run():
        output_path = None
        try:
            output_path = make_session_preview(filenames)
            post_file_to_channel_or_thread(
                interaction.channel_id,
                output_path,
                f"Session {session_index + 1} preview",
            )
        except Exception as e:
            logger.error("Session preview failed: %s", e)
            interaction.update_with_message(f"Preview failed: {e}")
        finally:
            _unlink_quiet(output_path)
            file_read_lock.release()

    threading.Thread(target=_run, daemon=True).start()
