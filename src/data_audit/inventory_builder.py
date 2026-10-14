# Dataset directory
#        ↓
# Recursive PNG discovery
#        ↓
# parse_mrl_filename(image_path)
#        ↓
# Valid metadata ────── Invalid-file report
#        ↓
# Dataset inventory

# Receive a dataset root directory
# Validate that the directory exists
# Discover .png files recursively
# Return the paths in a deterministic order
# Ignore non-PNG files

from pathlib import Path

from src.data_audit.filename_parser import parse_mrl_filename

ALLOWED_EXTENSIONS = {".png"}

# 1. Recursively discover files
# 2. Keep only files with supported extensions
# 3. Normalize extensions with .lower()
# 4. Sort the result
# 5. Return the list

def discover_image_files(dataset_root: str | Path) -> list:

    root = Path(dataset_root)
    if not root.exists():
        raise FileNotFoundError(f"Dataset root does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Dataset root is not a directory: {root}")
    
    image_paths = []
    for path in root.rglob("*"):
        if path.is_file():
            extension = path.suffix.lower()
            if extension in ALLOWED_EXTENSIONS:
                image_paths.append(path)

    image_paths.sort()
    return image_paths

def build_dataset_inventory(dataset_root: str | Path,)-> list:
    root = Path(dataset_root)
    image_paths = discover_image_files(root)
    metadata_inventory = []
    for image_path in image_paths:
        one_metadata = parse_mrl_filename(image_path)
        one_metadata['relative_path'] = str(image_path.relative_to(root))
        metadata_inventory.append(one_metadata)
    return metadata_inventory