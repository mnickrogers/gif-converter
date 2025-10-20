"""
Utility functions for video2gif tool.
Handles file validation, path operations, and helper functions.
"""

import os
import subprocess
from pathlib import Path

# Common video file extensions
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.webm', '.m4v', '.mpeg', '.mpg'}

def validate_video_file(filepath):
    """
    Validate that a file exists and is a supported video format.
    
    Args:
        filepath: Path to the video file
        
    Returns:
        Path object if valid
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not a supported video format
    """
    path = Path(filepath)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    if not path.is_file():
        raise ValueError(f"Not a file: {filepath}")
    
    if path.suffix.lower() not in VIDEO_EXTENSIONS:
        raise ValueError(f"Unsupported file format: {path.suffix}. Supported formats: {', '.join(VIDEO_EXTENSIONS)}")
    
    return path

def get_video_duration(filepath):
    """
    Get the duration of a video file in seconds using ffprobe.
    
    Args:
        filepath: Path to the video file
        
    Returns:
        Duration in seconds as float, or None if unable to determine
    """
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', str(filepath)],
            capture_output=True,
            text=True,
            check=True
        )
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        return None

def get_output_path(input_path, output_arg, batch_mode=False):
    """
    Determine the output path for a GIF file.
    
    Args:
        input_path: Path object of input video
        output_arg: User-specified output path (can be file or directory)
        batch_mode: Whether processing multiple files
        
    Returns:
        Path object for output GIF file
    """
    if output_arg:
        output = Path(output_arg)
        
        # If output is a directory, create output file in that directory
        if output.is_dir() or (batch_mode and not output.suffix):
            output.mkdir(parents=True, exist_ok=True)
            return output / f"{input_path.stem}.gif"
        
        # If output is a file path, use it directly (but only for single file mode)
        if not batch_mode:
            output.parent.mkdir(parents=True, exist_ok=True)
            return output
        
        # Batch mode with file specified - use as directory
        output.mkdir(parents=True, exist_ok=True)
        return output / f"{input_path.stem}.gif"
    
    # No output specified - use same directory as input
    return input_path.parent / f"{input_path.stem}.gif"

def format_size(size_bytes):
    """Format byte size as human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def check_ffmpeg_installed():
    """
    Check if FFmpeg is installed and available.
    
    Returns:
        True if FFmpeg is available, False otherwise
    """
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def expand_file_patterns(patterns):
    """
    Expand file patterns (including wildcards) into list of file paths.
    
    Args:
        patterns: List of file paths or patterns
        
    Returns:
        List of Path objects
    """
    from glob import glob
    
    files = []
    for pattern in patterns:
        # Check if pattern contains wildcards
        if '*' in pattern or '?' in pattern:
            matched = glob(pattern)
            files.extend([Path(f) for f in matched])
        else:
            files.append(Path(pattern))
    
    return files

