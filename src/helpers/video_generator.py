import os
import numpy as np
from multiprocessing import Pool
from typing import Dict, List

from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip, VideoClip

from src.helpers.combo_notation_generator import ComboNotationGenerator
from src.helpers.resource_loader import ResourceLoader

type FileMetaData = Dict[str, str]


class VideoGenerator:
    SOURCE_VIDEO_EXT = '.mp4'
    FILENAME_METADATA_KEYS = ['arena', 'starter', 'position', 'damage', 'inputs', 'comment']

    BACKGROUND_OFFSET_X = 280
    BACKGROUND_OFFSET_Y = 100

    COMBO_NAME_OFFSET_X = 290
    COMBO_NAME_OFFSET_Y = 100

    COMBO_DAMAGE_OFFSET_X = 1530
    COMBO_DAMAGE_OFFSET_Y = 100

    COMBO_NOTATION_OFFSET_X = 290
    COMBO_NOTATION_OFFSET_Y = 140

    COMMENT_PADDING_X = 10
    COMMENT_PADDING_Y = 10
    COMMENT_OFFSET_X = 1645
    COMMENT_OFFSET_Y = 185
    COMMENT_BACKGROUND_RGB = (142, 6, 59)

    def __init__(self, source_dir: str, out_dir: str):
        self.resource_loader = ResourceLoader()
        self.combo_notation_generator = ComboNotationGenerator(self.resource_loader)

        self.source_dir = source_dir
        self.out_dir = out_dir

    def process_video(self, filename: str) -> None:
        clip = VideoFileClip(os.path.join(self.source_dir, filename))
        metadata = self.__get_metadata_from_filename(filename)
        overlay = self.__generate_overlay(clip, metadata)

        CompositeVideoClip([clip, *overlay]).set_duration(clip.duration).write_videofile(
            os.path.join(self.out_dir, filename),
            codec='libx264',
            fps=60
        )

    def process_videos(self, filenames: List[str]) -> None:
        with Pool(os.cpu_count() / 2) as pool:
            pool.map(self.process_video, filenames)

    def regenerate_videos(self) -> None:
        self.process_videos(
            [filename for filename in os.listdir(self.source_dir) if filename.endswith(self.SOURCE_VIDEO_EXT)])

    def generate_new_videos(self) -> None:
        source_filenames = set(
            filename for filename in os.listdir(self.source_dir) if filename.endswith(self.SOURCE_VIDEO_EXT))
        out_filenames = set(
            filename for filename in os.listdir(self.out_dir) if filename.endswith(self.SOURCE_VIDEO_EXT))
        new_filenames = list(source_filenames - out_filenames)

        if len(new_filenames) == 0:
            print('Nothing to do')
            return

        self.process_videos(new_filenames)

    def __get_metadata_from_filename(self, filename: str) -> FileMetaData:
        name_without_ext = os.path.splitext(filename)[0]
        parts = name_without_ext.split("_")

        metadata = {}

        for i, key in enumerate(self.FILENAME_METADATA_KEYS):
            if i < len(parts) and parts[i]:
                metadata[key] = parts[i][1:-1]
            else:
                metadata[key] = ''

        return metadata

    def __generate_overlay(self, clip: VideoClip, metadata: FileMetaData) -> List[VideoClip]:
        overlay = []

        background_clip = self.resource_loader.get('background')
        overlay.append(background_clip.set_position((self.BACKGROUND_OFFSET_X, self.BACKGROUND_OFFSET_Y)))

        combo_name_clip = self.resource_loader.get(metadata['position'])
        overlay.append(combo_name_clip.set_position((self.COMBO_NAME_OFFSET_X, self.COMBO_NAME_OFFSET_Y)))

        combo_damage_clip = self.resource_loader.get(f'{metadata['damage']} Damage')
        overlay.append(combo_damage_clip.set_position((self.COMBO_DAMAGE_OFFSET_X, self.COMBO_DAMAGE_OFFSET_Y)))

        comment_clip = self.__generate_comment_clip(metadata['comment'])
        if comment_clip:
            overlay.append(comment_clip)

        combo_notation_clip = self.combo_notation_generator.generate_clip(
            clip, metadata['inputs']
        ).set_position((self.COMBO_NOTATION_OFFSET_X, self.COMBO_NOTATION_OFFSET_Y))
        overlay.append(combo_notation_clip)

        return overlay

    def __generate_comment_clip(self, comment: str) -> CompositeVideoClip or None:
        if not comment:
            return None

        comment_clip = self.resource_loader.get(comment)
        block_width = comment_clip.w + self.COMMENT_PADDING_X
        block_height = comment_clip.h + self.COMMENT_PADDING_Y
        comment_x = self.COMMENT_OFFSET_X - block_width
        comment_y = self.COMMENT_OFFSET_Y

        rectangle = np.zeros((block_height, block_width, 3), dtype=np.uint8)
        [r, g, b] = self.COMMENT_BACKGROUND_RGB
        rectangle[:, :, 0] = r
        rectangle[:, :, 1] = g
        rectangle[:, :, 2] = b

        background_clip = ImageClip(rectangle)

        comment_with_background = CompositeVideoClip(
            [background_clip, comment_clip.set_position((self.COMMENT_PADDING_X / 2, self.COMMENT_PADDING_Y / 2))],
            size=(block_width, block_height))

        return comment_with_background.set_position((comment_x, comment_y))
