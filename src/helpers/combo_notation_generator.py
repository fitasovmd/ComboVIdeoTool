from typing import Dict
from moviepy.editor import clips_array, VideoClip, CompositeVideoClip
from src.helpers.resource_loader import ResourceLoader

type Token = str
type Move = [Token]
type Combo = [Move]


class ComboNotationGenerator:
    DIRECTIONS = [
        'n', 'up', 'dp', 'bp', 'fp', 'ub', 'ubp', 'uf', 'ufp',
        'db', 'dbp', 'df', 'dfp', 'u', 'b', 'd', 'fff', 'ff', 'f',
    ]
    SEPARATOR = 'separator'
    NOTATION_MAX_WIDTH_PX = 1100
    TRANSITION_DURATION_S = 0.4

    clips: Dict[str, VideoClip] = {}

    def __init__(self, resource_loader: ResourceLoader):
        self.resource_loader = resource_loader

    def generate_clip(self, combo_clip: VideoClip, inputs: str) -> VideoClip:
        parsed_combo = self.__inputs_to_combo(inputs)

        clip_groups = []
        current_group = []
        current_width = 0

        separator_clip = self.resource_loader.get(self.SEPARATOR)

        for i, move in enumerate(parsed_combo):
            if current_width > self.NOTATION_MAX_WIDTH_PX:
                clip_groups.append(current_group)
                current_group = [separator_clip]
                current_width = separator_clip.w

            for token in move:
                token_clip = self.resource_loader.get(token)

                current_width += token_clip.w
                current_group.append(token_clip)

            if i != len(parsed_combo) - 1:
                current_width += separator_clip.w
                current_group.append(separator_clip)

        if current_group:
            clip_groups.append(current_group)

        total_width = sum(sum(clip.w for clip in group) for group in clip_groups)
        durations = [sum(clip.w for clip in group) / total_width * combo_clip.duration for group in clip_groups]

        final_clips = []
        start_time = 0
        for i, (group, duration) in enumerate(zip(clip_groups, durations)):
            group_clip = clips_array([group]).set_duration(duration)
            if i < len(clip_groups) - 1:
                next_group_clip = (clips_array([clip_groups[i + 1]])
                                   .set_duration(durations[i + 1]))
                group_clip = CompositeVideoClip([
                    group_clip.set_duration(duration - self.TRANSITION_DURATION_S)
                    .crossfadeout(self.TRANSITION_DURATION_S),
                    next_group_clip.set_start(duration - self.TRANSITION_DURATION_S)
                    .crossfadein(self.TRANSITION_DURATION_S)
                ])
            group_clip = group_clip.set_start(start_time)
            final_clips.append(group_clip)
            start_time += duration

        return CompositeVideoClip(final_clips).set_duration(combo_clip.duration)

    def __inputs_to_combo(self, inputs: str) -> Combo:

        combo = []

        for move in inputs.split(';'):
            move = move.strip()
            buttons = []
            for token in move.split(','):
                token = token.strip()
                for direction in self.DIRECTIONS:

                    if token.startswith(direction):
                        if token != direction:
                            buttons.append(direction)
                            buttons.append(token.split(direction)[1])
                        else:
                            buttons.append(token)
                        break
                else:
                    if token.startswith('{') and token.endswith('}'):
                        buttons.append(token[1:-1])
                    else:
                        buttons.append(token)

            combo.append(buttons)

        return combo
