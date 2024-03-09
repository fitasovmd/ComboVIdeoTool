import os
from typing import Dict
from moviepy.editor import TextClip, ImageClip, VideoClip


class ResourceLoader:
    IMAGE_EXT = 'png'
    TEXT_CLIP_OPTIONS = {
        'fontsize': 24,
        'font': 'Motorway-Bold',
        'color': 'White'
    }
    SCALING = 0.05
    IGNORE_SCALING = ['t', 'separator', 'background']

    CACHE: Dict[str, VideoClip] = {}

    def __init__(self):
        self.resources_dir = os.path.join(os.path.dirname(__file__), '../../resources')
        self.resources = [
            os.path.splitext(file)[0]
            for file in os.listdir(self.resources_dir)
            if file.endswith(self.IMAGE_EXT)
        ]

    def get(self, token: str):
        clip = self.CACHE.get(token)
        if clip:
            return clip

        if token in self.resources:
            if token in self.IGNORE_SCALING:
                clip = ImageClip(os.path.join(self.resources_dir, f'{token}.{self.IMAGE_EXT}'))
            else:
                clip = ImageClip(os.path.join(self.resources_dir, f'{token}.{self.IMAGE_EXT}')).resize(self.SCALING)
        else:
            clip = TextClip(token, **self.TEXT_CLIP_OPTIONS)

        self.CACHE[token] = clip
        return clip


