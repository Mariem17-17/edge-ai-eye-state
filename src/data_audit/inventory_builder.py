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

from PIL import Image, UnidentifiedImageError

ALLOWED_EXTENSIONS = {".png"}

# 1. Recursively discover files
# 2. Keep only files with supported extensions
# 3. Normalize extensions with .lower()
# 4. Sort the result
# 5. Return the list

def discover_image_files(dataset_root: str | Path) -> list:
    """
    Return a sorted list of supported image files found recursively
    under the dataset root.

    Raises FileNotFoundError if the path does not exist and
    NotADirectoryError if the path is not a directory.
    """    
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

def build_dataset_inventory(dataset_root: str | Path,) -> tuple[list[dict], list[dict]] :
    """
    Build inventory records from dataset images.

    Returns valid metadata records and filename-parsing failures
    as two separate lists.
    """
    root = Path(dataset_root)
    image_paths = discover_image_files(root)
    metadata_inventory = []
    failures = []
    for image_path in image_paths:
        relative_path = str(image_path.relative_to(root))
        try:
            one_metadata = parse_mrl_filename(image_path)
        except ValueError as exc:
            failure = {
                "relative_path": relative_path,
                "stage": "filename_parsing",
                "error": str(exc),
            }

            failures.append(failure)
            continue
        try:
            image_info = inspect_image_file(image_path)
        except ValueError as exc:
            failure = {
                "relative_path": relative_path,
                "stage": "image_inspection",
                "error": str(exc),
            }
            failures.append(failure)
            continue
        one_metadata["relative_path"] = relative_path
        one_metadata = one_metadata |image_info
        metadata_inventory.append(one_metadata)

    return metadata_inventory, failures


def inspect_image_file(image_path: str | Path) -> dict:
    """
    Inspect an image and return its dimensions, mode, channel count,
    and file size.

    Raises an error if the path is invalid or the image cannot be read.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file does not exist: {path}")
    if not path.is_file():
        raise IsADirectoryError(f"Image path is not a file: {path}")
    
    try:
        with Image.open(path) as image:
            image.load()
            image_info = {
                "width" : image.width,
                "height" : image.height,
                "channels" : len(image.getbands()),
                "image_mode" : image.mode,
                "file_size_bytes" : path.stat().st_size
                }
        
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(f"Unable to read image file {path}") from exc
        
    return image_info
