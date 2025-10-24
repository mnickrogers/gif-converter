"""
Quality presets for video to GIF conversion.
Each preset defines default parameters for fps, width, and color palette size.
"""

PRESETS = {
    'low': {
        'fps': 10,
        'width': 480,
        'colors': 128,
        'description': 'Small file size, lower quality'
    },
    'medium': {
        'fps': 15,
        'width': 720,
        'colors': 256,
        'description': 'Balanced quality and file size'
    },
    'high': {
        'fps': 20,
        'width': 1080,
        'colors': 256,
        'description': 'High quality, larger file size'
    },
    'max': {
        'fps': 30,
        'width': 2160,
        'colors': 256,
        'description': 'Maximum quality, very large file size'
    }
}

def get_preset(quality):
    """Get preset configuration by quality level."""
    if quality not in PRESETS:
        raise ValueError(f"Invalid quality preset: {quality}. Choose from: {', '.join(PRESETS.keys())}")
    return PRESETS[quality].copy()

def list_presets():
    """Return a formatted string of available presets."""
    lines = []
    for name, config in PRESETS.items():
        lines.append(f"  {name:8} - {config['description']}")
    return "\n".join(lines)

