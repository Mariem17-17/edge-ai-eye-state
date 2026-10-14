# Dataset Audit

Before training, I checked the dataset for:

- Unreadable or corrupted images
- Invalid filenames and metadata
- Class and subject distribution
- Exact duplicate files
- Subject overlap between splits
- Potential near-duplicate frames

The final train, validation, and test sets were created at subject level
to prevent the same person from appearing in multiple splits.

## Results

To be completed after running the audit.