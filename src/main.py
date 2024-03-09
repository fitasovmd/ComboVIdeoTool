from moviepy.config import change_settings
from helpers.video_generator import VideoGenerator

change_settings({'IMAGEMAGICK_BINARY': r'C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe'})

if __name__ == '__main__':
    generator = VideoGenerator(source_dir=r'D:\NVIDIA\Polaris',
                               out_dir=r'D:\Projects\Youtube\Viktor\generated_videos')
    generator.generate_new_videos()
