#!/usr/bin/env python3
"""
video2gif - Convert video files to optimized GIF animations.

A command-line tool that uses FFmpeg's two-pass palette generation
for high-quality GIF conversion with smart defaults and size targeting.
"""

import argparse
import sys
from pathlib import Path

from presets import PRESETS, get_preset, list_presets
from converter import VideoToGifConverter
from utils import (
    validate_video_file,
    get_output_path,
    check_ffmpeg_installed,
    expand_file_patterns,
    format_size,
    get_video_duration,
    get_video_fps
)

def create_parser():
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description='Convert video files to optimized GIF animations using FFmpeg.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Quality Presets:
{list_presets()}

Examples:
  # Convert single video with medium quality
  video2gif input.mp4

  # Convert with high quality preset
  video2gif input.mp4 -q high

  # Convert with maximum quality (source fps, 4K resolution)
  video2gif input.mp4 -q max

  # Convert and ensure output is under 5MB
  video2gif input.mp4 --max-size 5

  # Convert multiple videos to a directory
  video2gif *.mp4 -o gifs/

  # Custom settings: 10fps, 600px wide
  video2gif input.mp4 --fps 10 --width 600

  # Trim video (first 10 seconds only)
  video2gif input.mp4 --start 0 --end 10
"""
    )
    
    # Positional arguments
    parser.add_argument(
        'input',
        nargs='+',
        help='Input video file(s). Supports wildcards (*.mp4)'
    )
    
    # Output options
    parser.add_argument(
        '-o', '--output',
        help='Output file or directory. If directory, preserves input filename(s)'
    )
    
    # Quality preset
    parser.add_argument(
        '-q', '--quality',
        choices=list(PRESETS.keys()),
        default='medium',
        help='Quality preset (default: medium)'
    )
    
    # Size targeting
    parser.add_argument(
        '--max-size',
        type=float,
        metavar='MB',
        help='Target maximum file size in megabytes. Tool will iteratively reduce quality to meet target.'
    )
    
    # Custom parameters (override preset)
    parser.add_argument(
        '--fps',
        type=int,
        metavar='N',
        help='Frames per second (overrides preset)'
    )
    
    parser.add_argument(
        '--width',
        type=int,
        metavar='PX',
        help='Output width in pixels (height auto-scaled to preserve aspect ratio, overrides preset)'
    )
    
    parser.add_argument(
        '--colors',
        type=int,
        metavar='N',
        help='Number of colors in palette: 2-256 (overrides preset)'
    )
    
    # Trimming
    parser.add_argument(
        '--start',
        type=float,
        metavar='SEC',
        help='Start time in seconds'
    )
    
    parser.add_argument(
        '--end',
        type=float,
        metavar='SEC',
        help='End time in seconds'
    )
    
    # Verbosity
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output (show FFmpeg commands)'
    )
    
    return parser

def apply_smart_defaults(config, input_path):
    """
    Apply smart defaults based on video properties.

    Args:
        config: Configuration dictionary
        input_path: Path to input video

    Returns:
        Updated configuration dictionary
    """
    # If fps is None, auto-detect from source video
    if config.get('fps') is None:
        source_fps = get_video_fps(input_path)
        if source_fps:
            # Cap at 50 fps to avoid extremely large files
            config['fps'] = min(int(source_fps), 50)
        else:
            # Fallback to 30 fps if detection fails
            config['fps'] = 30

    # Get video duration for smart FPS adjustment
    duration = get_video_duration(input_path)

    if duration:
        # For very short videos (< 3s), increase FPS slightly for smoother playback
        if duration < 3 and config.get('fps') and config.get('fps') < 30:
            config['fps'] = min(config['fps'] + 5, 30)

    return config

def process_video(input_path, output_path, config):
    """
    Process a single video file.
    
    Args:
        input_path: Path to input video
        output_path: Path for output GIF
        config: Configuration dictionary
        
    Returns:
        True if successful, False otherwise
    """
    print(f"Converting: {input_path.name}")
    
    # Apply smart defaults
    config = apply_smart_defaults(config, input_path)
    
    # Create converter
    converter = VideoToGifConverter(input_path, output_path, config)
    
    # Convert with or without size targeting
    if config.get('max_size'):
        success = converter.convert_with_size_target(config['max_size'])
    else:
        success = converter.convert()
    
    if success:
        file_size = output_path.stat().st_size
        print(f"✓ Created: {output_path} ({format_size(file_size)})")
        return True
    else:
        print(f"✗ Failed: {input_path.name}")
        return False

def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Check FFmpeg installation
    if not check_ffmpeg_installed():
        print("Error: FFmpeg is not installed or not in PATH.", file=sys.stderr)
        print("Please install FFmpeg: https://ffmpeg.org/download.html", file=sys.stderr)
        if sys.platform == 'darwin':
            print("On macOS, you can install with: brew install ffmpeg", file=sys.stderr)
        sys.exit(1)
    
    # Expand file patterns (wildcards)
    input_files = expand_file_patterns(args.input)
    
    if not input_files:
        print("Error: No input files specified.", file=sys.stderr)
        sys.exit(1)
    
    # Validate all input files first
    validated_files = []
    for input_file in input_files:
        try:
            validated_files.append(validate_video_file(input_file))
        except (FileNotFoundError, ValueError) as e:
            print(f"Warning: {e}", file=sys.stderr)
    
    if not validated_files:
        print("Error: No valid video files to process.", file=sys.stderr)
        sys.exit(1)
    
    # Build configuration from preset and overrides
    config = get_preset(args.quality)
    
    # Apply command-line overrides
    if args.fps:
        config['fps'] = args.fps
    if args.width:
        config['width'] = args.width
    if args.colors:
        if args.colors < 2 or args.colors > 256:
            print("Error: colors must be between 2 and 256", file=sys.stderr)
            sys.exit(1)
        config['colors'] = args.colors
    if args.start is not None:
        config['start'] = args.start
    if args.end is not None:
        config['end'] = args.end
    if args.max_size:
        config['max_size'] = args.max_size
    
    config['verbose'] = args.verbose
    
    # Process files
    batch_mode = len(validated_files) > 1
    success_count = 0
    
    print(f"\nProcessing {len(validated_files)} file(s) with quality preset: {args.quality}")
    print(f"Settings: fps={config['fps']}, width={config['width']}, colors={config['colors']}")
    if args.max_size:
        print(f"Target size: {args.max_size} MB")
    print()
    
    for input_path in validated_files:
        output_path = get_output_path(input_path, args.output, batch_mode)
        
        if process_video(input_path, output_path, config.copy()):
            success_count += 1
        print()  # Blank line between files
    
    # Summary
    if batch_mode:
        print(f"Completed: {success_count}/{len(validated_files)} files converted successfully")
    
    sys.exit(0 if success_count > 0 else 1)

if __name__ == '__main__':
    main()

