from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class VideoProvider(ABC):
    @abstractmethod
    def generate(self, **kwargs):
        ...

    @abstractmethod
    def get_status(self, job_id: str):
        ...

    @abstractmethod
    def cancel(self, job_id: str):
        ...

    @abstractmethod
    def get_result(self, job_id: str):
        ...


class ImageProvider(ABC):
    @abstractmethod
    def generate(self, **kwargs):
        ...

    @abstractmethod
    def get_status(self, job_id: str):
        ...

    @abstractmethod
    def get_result(self, job_id: str):
        ...


class AudioProvider(ABC):
    @abstractmethod
    def generate(self, **kwargs):
        ...


class VoiceProvider(ABC):
    @abstractmethod
    def generate(self, **kwargs):
        ...


class UpscaleProvider(ABC):
    @abstractmethod
    def upscale(self, **kwargs):
        ...


class ModerationProvider(ABC):
    @abstractmethod
    def check_prompt(self, prompt: str):
        ...

    @abstractmethod
    def check_image(self, image_url: str):
        ...

    @abstractmethod
    def check_video(self, video_url: str):
        ...
