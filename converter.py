"""
Core video to GIF converter using FFmpeg.
Implements two-pass palette generation for optimal quality.
"""

import subprocess
import tempfile
import os
from pathlib import Path
from utils import get_video_duration, format_size

class VideoToGifConverter:
    """Handles video to GIF conversion using FFmpeg."""
    
    def __init__(self, input_path, output_path, config):
        """
        Initialize converter with paths and configuration.
        
        Args:
            input_path: Path to input video file
            output_path: Path for output GIF file
            config: Dictionary with conversion parameters (fps, width, colors, etc.)
        """
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.config = config
        self.verbose = config.get('verbose', False)
        
    def _build_filter_string(self, palette_mode=False):
        """
        Build FFmpeg filter string for scaling and palette generation.
        
        Args:
            palette_mode: If True, build filter for palette generation
            
        Returns:
            FFmpeg filter string
        """
        filters = []
        
        # Trimming
        if self.config.get('start') or self.config.get('end'):
            trim_filter = "trim="
            if self.config.get('start'):
                trim_filter += f"start={self.config['start']}"
            if self.config.get('end'):
                if self.config.get('start'):
                    trim_filter += ":"
                trim_filter += f"end={self.config['end']}"
            trim_filter += ",setpts=PTS-STARTPTS"
            filters.append(trim_filter)
        
        # FPS
        fps = self.config.get('fps', 15)
        filters.append(f"fps={fps}")
        
        # Scaling
        width = self.config.get('width')
        if width:
            # Preserve aspect ratio, ensure even dimensions
            filters.append(f"scale={width}:-2:flags=lanczos")
        
        if palette_mode:
            # Palette generation
            colors = self.config.get('colors', 256)
            filters.append(f"palettegen=max_colors={colors}:stats_mode=diff")
        else:
            # Use palette for final GIF
            filters.append("[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5")
        
        return ",".join(filters)
    
    def _generate_palette(self, palette_path):
        """
        First pass: Generate optimized color palette.
        
        Args:
            palette_path: Path to save the palette file
            
        Returns:
            True if successful, False otherwise
        """
        filter_string = self._build_filter_string(palette_mode=True)
        
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output file
            '-i', str(self.input_path),
            '-vf', filter_string,
            str(palette_path)
        ]
        
        if not self.verbose:
            cmd.extend(['-loglevel', 'error'])
        
        try:
            if self.verbose:
                print(f"  Generating palette...")
                print(f"  Command: {' '.join(cmd)}")
            
            subprocess.run(cmd, check=True, capture_output=not self.verbose)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error generating palette: {e}")
            return False
    
    def _create_gif(self, palette_path):
        """
        Second pass: Create GIF using the generated palette.
        
        Args:
            palette_path: Path to the palette file
            
        Returns:
            True if successful, False otherwise
        """
        filter_string = self._build_filter_string(palette_mode=False)
        
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output file
            '-i', str(self.input_path),
            '-i', str(palette_path),
            '-lavfi', filter_string,
            str(self.output_path)
        ]
        
        if not self.verbose:
            cmd.extend(['-loglevel', 'error'])
        
        try:
            if self.verbose:
                print(f"  Creating GIF...")
                print(f"  Command: {' '.join(cmd)}")
            
            subprocess.run(cmd, check=True, capture_output=not self.verbose)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error creating GIF: {e}")
            return False
    
    def convert(self):
        """
        Perform two-pass conversion: palette generation + GIF creation.
        
        Returns:
            True if successful, False otherwise
        """
        # Create temporary palette file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as palette_file:
            palette_path = palette_file.name
        
        try:
            # Pass 1: Generate palette
            if not self._generate_palette(palette_path):
                return False
            
            # Pass 2: Create GIF
            if not self._create_gif(palette_path):
                return False
            
            return True
        finally:
            # Clean up palette file
            try:
                os.unlink(palette_path)
            except OSError:
                pass
    
    def convert_with_size_target(self, max_size_mb):
        """
        Convert video to GIF with file size constraint.
        Iteratively adjusts parameters if initial conversion exceeds target size.
        
        Args:
            max_size_mb: Maximum file size in megabytes
            
        Returns:
            True if successful, False otherwise
        """
        max_size_bytes = max_size_mb * 1024 * 1024
        
        # Try initial conversion
        if self.verbose:
            print(f"  Target size: {max_size_mb} MB")
        
        if not self.convert():
            return False
        
        # Check file size
        current_size = self.output_path.stat().st_size
        
        if current_size <= max_size_bytes:
            if self.verbose:
                print(f"  ✓ Size: {format_size(current_size)} (within target)")
            return True
        
        # File too large - need to reduce size
        print(f"  Initial size {format_size(current_size)} exceeds target {max_size_mb} MB, optimizing...")
        
        # Strategy: reduce fps and/or width iteratively
        original_fps = self.config.get('fps', 15)
        original_width = self.config.get('width')
        
        attempts = [
            # Try reducing FPS first
            {'fps': max(5, int(original_fps * 0.75)), 'width': original_width},
            {'fps': max(5, int(original_fps * 0.5)), 'width': original_width},
            # Then reduce both FPS and width
            {'fps': max(5, int(original_fps * 0.75)), 'width': int(original_width * 0.75) if original_width else None},
            {'fps': max(5, int(original_fps * 0.5)), 'width': int(original_width * 0.75) if original_width else None},
            {'fps': max(5, int(original_fps * 0.5)), 'width': int(original_width * 0.5) if original_width else None},
        ]
        
        for i, adjustment in enumerate(attempts, 1):
            if self.verbose:
                print(f"  Attempt {i}: fps={adjustment['fps']}, width={adjustment['width']}")
            
            # Update config with new parameters
            self.config.update(adjustment)
            
            # Convert again
            if not self.convert():
                return False
            
            # Check new size
            current_size = self.output_path.stat().st_size
            
            if current_size <= max_size_bytes:
                print(f"  ✓ Optimized to {format_size(current_size)} (fps={adjustment['fps']}, width={adjustment['width']})")
                return True
        
        # Still too large after all attempts
        print(f"  ⚠ Unable to reduce size below {max_size_mb} MB. Final size: {format_size(current_size)}")
        print(f"  Consider using a lower quality preset or manually specifying smaller dimensions.")
        return True  # Still return True as conversion succeeded, just not the size target

