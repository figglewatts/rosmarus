from .. import resources
from .. import audio


def load_sound(path: str) -> audio.AudioClip:
    return audio.AudioClip(path)


def cleanup_sound(audio_clip: audio.AudioClip) -> None:
    audio_clip.cleanup()


resources.register_type_handler("sound", load_sound, cleanup_sound)