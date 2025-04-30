from PIL import Image
import os
from pathlib import Path

# Get base directory
base_dir = str(Path(__file__).resolve().parent.parent)

# Path to input PNG file
png_path = os.path.join(base_dir, 'resources', 'tray_icon.png')

# Path for output ICO file
ico_path = os.path.join(base_dir, 'resources', 'tray_icon.ico')

# Open the PNG image
img = Image.open(png_path)

# Convert and save as ICO
img.save(ico_path, format='ICO')

print(f"Converted {png_path} to {ico_path}")
