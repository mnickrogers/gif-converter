# Quick Start Guide

## Installation

1. Install FFmpeg:
   ```bash
   brew install ffmpeg  # macOS
   ```

2. No Python packages needed - uses standard library only!

## Common Commands

### Basic conversion
```bash
python video2gif.py myvideo.mp4
```

### High quality
```bash
python video2gif.py myvideo.mp4 -q high
```

### Limit file size to 5MB
```bash
python video2gif.py myvideo.mp4 --max-size 5
```

### Convert multiple files
```bash
python video2gif.py *.mp4 -o gifs/
```

### Trim video (first 10 seconds)
```bash
python video2gif.py myvideo.mp4 --start 0 --end 10
```

### Custom settings
```bash
python video2gif.py myvideo.mp4 --fps 10 --width 600
```

## Quality Presets

- **low**: 10fps, 480px, 128 colors (small files)
- **medium**: 15fps, 720px, 256 colors (default, balanced)
- **high**: 20fps, 1080px, 256 colors (best quality)
- **max**: 30fps, 2160px, 256 colors (maximum quality, very large files)

## Tips

- Start with `-q medium` (default)
- Use `--max-size` for sharing (e.g., `--max-size 10` for Slack)
- Test settings on short clips first with `--start` and `--end`
- Use `-v` for verbose output if something goes wrong

See README.md for full documentation!

