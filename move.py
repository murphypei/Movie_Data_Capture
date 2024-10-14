import shutil
from pathlib import Path


def move_video_files(src_dir: str, dest_dir: str, video_extensions=None):
    if video_extensions is None:
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.mpg', '.mpeg'}
    
    # 定义源目录和目标目录
    src_path = Path(src_dir)
    dest_path = Path(dest_dir)
    
    # 确保目标目录存在
    dest_path.mkdir(parents=True, exist_ok=True)
    
    # 遍历源目录中的所有文件和子目录
    for file in src_path.rglob('*'):
        if file.is_file() and file.suffix.lower() in video_extensions:
            try:
                # 移动文件到目标目录
                shutil.move(str(file), dest_path / file.name)
                print(f"Moved: {file}")
            except Exception as e:
                print(f"Error moving {file}: {e}")

# 使用示例
source_directory = r'G:\output'
destination_directory = r'G:\JAV'
move_video_files(source_directory, destination_directory)
