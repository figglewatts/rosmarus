from .. import resources
from .. import audio


def load_music(path: str) -> audio.AudioStream:
    return audio.AudioStream(path)


def cleanup_music(audio_stream: audio.AudioStream) -> None:
    audio_stream.cleanup()


resources.register_type_handler("music", load_music, cleanup_music)