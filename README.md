# video2gif

A command-line tool for converting videos to high-quality GIF animations using FFmpeg's two-pass palette generation.

## Features

- 🎨 **High-quality output** - Uses FFmpeg's two-pass palette generation for optimal color reproduction
- 📦 **Quality presets** - Simple low/medium/high presets with smart defaults
- 🎯 **Size targeting** - Automatically optimize to meet file size constraints
- 🔄 **Batch processing** - Convert multiple videos with a single command
- ⚙️ **Flexible controls** - Override presets with custom FPS, width, colors
- ✂️ **Video trimming** - Extract specific time ranges
- 🧠 **Smart defaults** - Automatically adjusts parameters based on video properties

## Installation

### Prerequisites

**FFmpeg must be installed on your system.**

On macOS:
```bash
brew install ffmpeg
```

On Ubuntu/Debian:
```bash
sudo apt-get install ffmpeg
```

On Windows:
Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

### Setup

1. Clone or download this repository
2. Navigate to the directory:
```bash
cd video2gif
```

3. Make the script executable (optional):
```bash
chmod +x video2gif.py
```

That's it! No Python dependencies needed - uses only standard library modules.

## Usage

### Basic Usage

Convert a video with default settings (medium quality):
```bash
python video2gif.py input.mp4
```

### Quality Presets

Use quality presets for quick conversions:

```bash
# Low quality (smaller file size)
python video2gif.py input.mp4 -q low

# Medium quality (balanced - default)
python video2gif.py input.mp4 -q medium

# High quality (larger file size)
python video2gif.py input.mp4 -q high

# Maximum quality (source fps, 4K resolution)
python video2gif.py input.mp4 -q max
```

**Preset specifications:**
- **low**: 10fps, 480px width, 128 colors
- **medium**: 15fps, 720px width, 256 colors
- **high**: 20fps, 1080px width, 256 colors
- **max**: source fps (auto-detected, capped at 50), 2160px width, 256 colors

### File Size Targeting

Ensure your GIF stays under a specific size:

```bash
# Keep output under 5MB
python video2gif.py input.mp4 --max-size 5

# Keep under 2MB with high quality preset as starting point
python video2gif.py input.mp4 -q high --max-size 2
```

The tool will automatically reduce FPS and/or resolution iteratively until the target size is met.

### Batch Processing

Convert multiple videos at once:

```bash
# Convert all MP4 files in current directory
python video2gif.py *.mp4 -o gifs/

# Convert specific files
python video2gif.py video1.mp4 video2.mov video3.avi -o output/

# High quality batch conversion with size limit
python video2gif.py *.mp4 -q high --max-size 10 -o gifs/
```

### Custom Parameters

Override preset defaults with custom values:

```bash
# Custom FPS and width
python video2gif.py input.mp4 --fps 10 --width 600

# Custom color palette size
python video2gif.py input.mp4 --colors 128

# Combine custom settings
python video2gif.py input.mp4 --fps 20 --width 1920 --colors 256
```

### Video Trimming

Extract specific time ranges:

```bash
# First 10 seconds
python video2gif.py input.mp4 --start 0 --end 10

# From 5s to 15s
python video2gif.py input.mp4 --start 5 --end 15

# From 30s to end
python video2gif.py input.mp4 --start 30
```

### Specify Output

Control where the GIF is saved:

```bash
# Specify output filename
python video2gif.py input.mp4 -o output.gif

# Save to different directory (preserves filename)
python video2gif.py input.mp4 -o ~/Desktop/

# Batch mode: save all to directory
python video2gif.py *.mp4 -o gifs/
```

### Verbose Mode

See detailed FFmpeg commands and processing info:

```bash
python video2gif.py input.mp4 -v
```

## Architecture

The tool is built with a modular architecture:

```
video2gif/
├── video2gif.py    # CLI interface and orchestration
├── converter.py    # Core FFmpeg conversion logic
├── presets.py      # Quality preset configurations
├── utils.py        # Helper functions and validation
└── README.md       # This file
```

### Two-Pass Conversion Process

1. **Pass 1 - Palette Generation**: Analyzes the video and generates an optimized 256-color palette
2. **Pass 2 - GIF Creation**: Uses the custom palette to create the final GIF with superior color accuracy

This approach produces significantly better quality than direct conversion.

### Size Targeting Algorithm

When `--max-size` is specified:
1. Performs initial conversion with requested settings
2. Checks output file size
3. If too large, iteratively reduces FPS and/or width
4. Tries up to 5 different parameter combinations
5. Reports final size and optimizations applied

## Examples

### Example 1: Quick Social Media GIF
```bash
python video2gif.py myvideo.mp4 -q medium --max-size 5 -o social.gif
```
Creates a ~5MB GIF optimized for social media sharing.

### Example 2: High-Quality Documentation GIF
```bash
python video2gif.py demo.mp4 -q high --fps 30 --width 1920
```
Creates a smooth, high-resolution GIF for documentation.

### Example 3: Batch Convert Clips
```bash
python video2gif.py clips/*.mp4 -q low --max-size 2 -o gifs/
```
Converts all videos in `clips/` directory to small, optimized GIFs.

### Example 4: Extract and Convert Scene
```bash
python video2gif.py movie.mp4 --start 125 --end 135 -q high -o scene.gif
```
Extracts a 10-second scene and converts it to high-quality GIF.

## Tips

- **Start with presets**: Use `-q low/medium/high` for quick results
- **Use size targeting for sharing**: `--max-size` ensures GIFs fit platform limits (e.g., 10MB for Slack)
- **Preview with trimming**: Use `--start` and `--end` to test settings on a short clip first
- **Batch processing**: Process multiple files efficiently with wildcards
- **Check verbose output**: Use `-v` to troubleshoot or understand what's happening

## Supported Formats

Input formats (any format supported by your FFmpeg installation):
- MP4, MOV, AVI, MKV, FLV, WMV, WebM, M4V, MPEG, MPG

Output format:
- GIF (optimized with custom color palette)

## Troubleshooting

**"FFmpeg is not installed"**
- Install FFmpeg using the instructions above
- Verify installation: `ffmpeg -version`

**GIF quality is poor**
- Try the `high` quality preset: `-q high`
- Increase colors: `--colors 256`
- Increase FPS: `--fps 20` or higher
- Ensure source video is high quality

**File size too large**
- Use `--max-size` to automatically optimize
- Use lower quality preset: `-q low`
- Reduce width: `--width 480`
- Reduce FPS: `--fps 10`

**Conversion is slow**
- This is normal - two-pass conversion prioritizes quality
- Process shorter clips: use `--start` and `--end`
- Use lower resolution: `--width 480`

