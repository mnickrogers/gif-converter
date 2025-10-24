# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

video2gif is a command-line tool for converting videos to high-quality GIF animations using FFmpeg's two-pass palette generation. The tool uses only Python standard library modules and requires FFmpeg to be installed on the system.

## Running the Tool

Basic conversion:
```bash
python video2gif.py input.mp4
```

With quality presets:
```bash
python video2gif.py input.mp4 -q high
```

With size targeting:
```bash
python video2gif.py input.mp4 --max-size 5
```

Batch processing:
```bash
python video2gif.py *.mp4 -o gifs/
```

Verbose mode (for debugging):
```bash
python video2gif.py input.mp4 -v
```

## Architecture

The codebase follows a modular architecture with clear separation of concerns:

### Core Modules

**video2gif.py** - CLI orchestration
- Entry point and argument parsing
- Batch file processing logic
- Smart defaults application based on video properties (e.g., increasing FPS for short videos)
- Configuration building from presets and CLI overrides

**converter.py** - FFmpeg conversion engine
- `VideoToGifConverter` class handles the two-pass conversion process
- Pass 1: Generates an optimized color palette using `palettegen`
- Pass 2: Creates the final GIF using the custom palette with `paletteuse`
- Size targeting algorithm: iteratively reduces FPS and/or width to meet file size constraints
- Attempts up to 5 different parameter combinations when optimizing for size

**presets.py** - Quality preset definitions
- Three presets: low (10fps, 480px, 128 colors), medium (15fps, 720px, 256 colors), high (20fps, 1080px, 256 colors)
- Presets serve as starting points that can be overridden via CLI arguments

**utils.py** - Helper functions
- File validation and path operations
- FFmpeg/ffprobe availability checking
- Video duration detection using ffprobe
- File pattern expansion for batch processing

### Key Design Patterns

**Two-Pass Conversion**: Always generates a custom palette first, then uses it for GIF creation. This produces significantly better color accuracy than direct conversion.

**Iterative Size Optimization**: When `--max-size` is specified, the tool tries progressively reduced parameters (FPS first, then width) until the target size is met or all attempts are exhausted.

**Filter Chain Construction**: FFmpeg filters are built dynamically based on configuration (trimming, FPS, scaling, palette operations). The filter string differs between palette generation and GIF creation passes.

## Dependencies

- Python 3.x with standard library only
- FFmpeg (must be installed separately on the system)
- ffprobe (typically included with FFmpeg)

No `pip install` is required. The empty package.json is not used by the tool.

## Making Changes

When modifying FFmpeg filter construction logic in `converter.py`, note that:
- Palette generation uses `palettegen=max_colors=N:stats_mode=diff`
- GIF creation combines base filters with `paletteuse=dither=bayer:bayer_scale=5`
- The filter string format differs between the two passes

When adding new quality presets in `presets.py`, ensure all three parameters are defined: fps, width, colors.

When modifying the size targeting algorithm in `converter.py:convert_with_size_target()`, the reduction strategy currently tries FPS reduction first, then combined FPS+width reduction in increasingly aggressive steps.
