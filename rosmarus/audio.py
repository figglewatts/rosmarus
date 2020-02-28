from __future__ import annotations
from abc import ABC, abstractmethod
from array import array
import ctypes as ct
import threading
import time
from typing import Union
import logging

import openal.al as al
import openal.alc as alc

from pyogg import VorbisFileStream, VorbisFile, vorbis, PYOGG_STREAM_BUFFER_SIZE


class _Audio:
    def __init__(self) -> None:
        self.device = None
        self.context = None
        self.sources = []


_audio = _Audio()

_AL_ERR_MAP = {
    al.AL_NO_ERROR: "AL_NO_ERROR",
    al.AL_INVALID_NAME: "AL_INVALID_NAME",
    al.AL_INVALID_ENUM: "AL_INVALID_ENUM",
    al.AL_INVALID_VALUE: "AL_INVALID_VALUE",
    al.AL_INVALID_OPERATION: "AL_INVALID_OPERATION",
    al.AL_OUT_OF_MEMORY: "AL_OUT_OF_MEMORY"
}

_ALC_ERR_MAP = {
    alc.ALC_NO_ERROR: "ALC_NO_ERROR",
    alc.ALC_INVALID_DEVICE: "ALC_INVALID_DEVICE",
    alc.ALC_INVALID_CONTEXT: "ALC_INVALID_CONTEXT",
    alc.ALC_INVALID_ENUM: "ALC_INVALID_ENUM",
    alc.ALC_INVALID_VALUE: "ALC_INVALID_VALUE",
    alc.ALC_OUT_OF_MEMORY: "ALC_OUT_OF_MEMORY"
}


class BaseAudio(ABC):
    @abstractmethod
    def __init__(self) -> None:
        self.attached_sources = {}

    def register_source(self, source: AudioSource) -> None:
        self.attached_sources[source.handle.value] = source

    def deregister_source(self, source: AudioSource) -> None:
        del self.attached_sources[source.handle.value]

    @abstractmethod
    def length_seconds(self) -> float:
        raise NotImplementedError()

    @abstractmethod
    def cleanup(self) -> None:
        raise NotImplementedError()


class AudioClip(BaseAudio):
    def __init__(self, file_path: str) -> None:
        super().__init__()
        self.clip = VorbisFile(file_path)
        self.handle = ct.c_uint(0)
        al.alGenBuffers(1, ct.byref(self.handle))
        self.format = al.AL_FORMAT_MONO16 if self.clip.channels == 1 \
            else al.AL_FORMAT_STEREO16
        al.alBufferData(self.handle, self.format, self.clip.buffer,
                        self.clip.buffer_length, self.clip.frequency)

    def length_seconds(self) -> float:
        return self.clip.buffer_length / (self.clip.frequency *
                                          self.clip.channels * 2)

    def cleanup(self) -> None:
        for source in self.attached_sources.values():
            source.stop()
        al.alDeleteBuffers(1, ct.byref(self.handle))


class AudioStream(BaseAudio):
    BUFFER_COUNT = 3

    def __init__(self, file_path: str) -> None:
        super().__init__()
        self.file_path = file_path
        self.clip = VorbisFileStream(file_path)
        self._length_seconds = vorbis.ov_time_total(self.clip.vf, -1)
        self.buffers = (ct.c_uint * AudioStream.BUFFER_COUNT)(0, 0, 0)
        self.format = al.AL_FORMAT_MONO16 if self.clip.channels == 1 \
            else al.AL_FORMAT_STEREO16
        for i in range(0, AudioStream.BUFFER_COUNT):
            buf_handle = ct.c_uint(0)
            al.alGenBuffers(1, ct.byref(buf_handle))
            self.buffers[i] = buf_handle
            self.fill_buffer(index=i)

    def _read_vorbis_data(self):
        # mostly lifted from https://github.com/Zuzu-Typ/PyOgg/blob/master/pyogg/__init__.py#L98
        buf = []
        total_written = 0

        while True:
            new_bytes = vorbis.ov_read(
                ct.byref(self.clip.vf), self.clip.buffer_,
                PYOGG_STREAM_BUFFER_SIZE * self.clip.channels - total_written,
                0, 2, 1, self.clip.bitstream_pointer)
            array_ = ct.cast(
                self.clip.buffer_,
                ct.POINTER(
                    ct.c_char *
                    (PYOGG_STREAM_BUFFER_SIZE * self.clip.channels))).contents

            buf.append(array_.raw[:new_bytes])
            total_written += new_bytes
            if new_bytes == 0 or total_written >= PYOGG_STREAM_BUFFER_SIZE * self.clip.channels:
                break

        out_buffer = b"".join(buf)

        if total_written == 0:
            return None

        return out_buffer, total_written

    def fill_buffer(self, index: int = None, handle: int = None) -> bool:
        buf_handle = handle
        if index is not None:
            buf_handle = self.buffers[index]
        if buf_handle is None:
            raise RuntimeError(
                "Call _fill_buffer() with either index or handle")
        data = self._read_vorbis_data()
        if data is None:
            return True
        buf, buf_len = data
        al.alBufferData(buf_handle, self.format, buf, buf_len,
                        self.clip.frequency)

    def seek_to_start(self) -> None:
        vorbis.ov_pcm_seek_lap(self.clip.vf, 0)

    def length_seconds(self) -> float:
        return self._length_seconds

    def cleanup(self) -> None:
        for source in self.attached_sources.values():
            source.stop()
        al.alDeleteBuffers(AudioStream.BUFFER_COUNT, self.buffers)
        self.clip.clean_up()


class AudioSource:
    def __init__(self) -> None:
        self.handle = ct.c_uint(0)
        self.playing = False
        self.paused = False
        self.looping = False
        self.clip = None
        self.finish_timer = None
        self.streaming = False
        self.stream_buffer_callback = None
        self.stop_streaming_event = threading.Event()
        self.time_played_for = None
        al.alGenSources(1, ct.byref(self.handle))

    def stream(self, stream: AudioStream, loop: bool = False) -> None:
        self.streaming = True
        self.clip = stream
        al.alSourceQueueBuffers(self.handle, AudioStream.BUFFER_COUNT,
                                stream.buffers)
        al.alSourcePlay(self.handle)
        stream.register_source(self)
        self.playing = True
        self.paused = False
        self.looping = loop
        self.time_played_for = time.time()

        self.stream_buffer_callback = threading.Thread(
            target=self._check_for_used_buffers)
        self.stream_buffer_callback.start()

        time_to_finish = stream.length_seconds()

        # start the timer to execute the callback
        if not loop:
            self.finish_timer = threading.Timer(time_to_finish,
                                                self._on_finish_play)
            self.finish_timer.start()

    def play(self, clip: AudioClip, loop: bool = False) -> None:
        self.clip = clip
        al.alSourcei(self.handle, al.AL_BUFFER, clip.handle.value)
        al.alSourcei(self.handle, al.AL_LOOPING, 1 if loop else 0)
        al.alSourcePlay(self.handle)
        clip.register_source(self)
        self.playing = True
        self.paused = False
        self.looping = loop
        self.time_played_for = time.time()

        if not loop:
            time_to_finish = clip.length_seconds()

            # start the timer to execute the callback
            self.finish_timer = threading.Timer(time_to_finish,
                                                self._on_finish_play)
            self.finish_timer.start()

    def resume(self) -> None:
        if not self.paused:
            return
        al.alSourcePlay(self.handle)

        if self.streaming:
            self.stream_buffer_callback = threading.Thread(
                target=self._check_for_used_buffers)
            self.stream_buffer_callback.start()

        if not self.looping:
            time_to_finish = self.clip.length_seconds() - self.time_played_for

            # start the timer to execute the callback
            self.finish_timer = threading.Timer(time_to_finish,
                                                self._on_finish_play)
            self.finish_timer.start()

    def pause(self) -> None:
        al.alSourcePause(self.handle)
        self.paused = True
        self.time_played_for = time.time() - self.time_played_for
        # our existing callback is invalid if we've paused, it won't know
        # that we've paused -- cancel it and we'll handle it when we play
        # again
        if self.finish_timer:
            self.finish_timer.cancel()
            self.finish_timer = None
        if self.stream_buffer_callback:
            self.stop_streaming_event.set()
            self.stream_buffer_callback.join()
            self.stop_streaming_event.clear()

    def stop(self) -> None:
        al.alSourceStop(self.handle)
        al.alSourcei(self.handle, al.AL_BUFFER, 0)
        if self.streaming:
            self.clip.seek_to_start()
        self.playing = False
        self.paused = False
        self.played_at = None
        self.looping = False
        self.clip = None
        self.time_played_for = 0
        self.streaming = False
        if self.finish_timer:
            self.finish_timer.cancel()
            self.finish_timer = None
        if self.stream_buffer_callback:
            self.stop_streaming_event.set()
            self.stream_buffer_callback.join()
            self.stop_streaming_event.clear()

    def cleanup(self) -> None:
        self.stop()
        al.alDeleteSources(1, ct.byref(self.handle))

    def _on_finish_play(self) -> None:
        self.clip.deregister_source(self)
        self.stop()

    def _check_for_used_buffers(self):
        while True:
            if self.stop_streaming_event.is_set():
                break

            buffers_processed = ct.c_int(0)
            al.alGetSourcei(self.handle, al.AL_BUFFERS_PROCESSED,
                            ct.byref(buffers_processed))
            while buffers_processed.value > 0:
                buffer_handle = ct.c_uint(0)
                al.alSourceUnqueueBuffers(self.handle, 1,
                                          ct.byref(buffer_handle))
                finished = self.clip.fill_buffer(handle=buffer_handle)
                if finished and self.looping:
                    self.clip.seek_to_start()
                    self.clip.fill_buffer(handle=buffer_handle)
                elif finished and not self.looping:
                    return
                al.alSourceQueueBuffers(self.handle, 1,
                                        ct.byref(buffer_handle))
                buffers_processed.value -= 1
            time.sleep(0.01)


def _check_err(context: str, alc: bool = False) -> None:
    error = al.alGetError()
    if error != al.AL_NO_ERROR:
        err_code = _ALC_ERR_MAP[error] if alc else _AL_ERR_MAP[error]
        raise RuntimeError(f"openal error while {context}: {err_code}")


def init() -> None:
    default_device = alc.alcGetString(None, alc.ALC_DEFAULT_DEVICE_SPECIFIER)
    _audio.device = alc.alcOpenDevice(default_device)
    if not _audio.device:
        raise RuntimeError("Unable to get audio device handle")

    _audio.context = alc.alcCreateContext(_audio.device, None)

    if not alc.alcMakeContextCurrent(_audio.context):
        _check_err("making context current", True)


def play(sound: Union[AudioClip, AudioStream],
         loop: bool = False) -> AudioSource:
    source = AudioSource()
    if isinstance(sound, AudioClip):
        source.play(sound, loop)
    elif isinstance(sound, AudioStream):
        source.stream(sound, loop)
    return source


def cleanup() -> None:
    alc.alcDestroyContext(_audio.context)
    alc.alcCloseDevice(_audio.device)