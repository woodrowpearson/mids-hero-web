"""Command-line interface for MHD parser."""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional, List

from .main_database_parser import parse_main_database
from .enhancement_database_parser import parse_enhancement_database
from .salvage_parser import parse_salvage_database
from .recipe_parser import parse_recipe_database
from .text_mhd_parser import parse_text_mhd, detect_file_format, FileFormat
from .json_exporter import MhdJsonExporter


# Configure logging
def setup_logging(level: str = "INFO") -> None:
    """Set up logging configuration."""
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


class MhdParserCLI:
    """Command-line interface for parsing MHD files."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.json_exporter = MhdJsonExporter()
    
    def parse_file(self, file_path: Path, output_dir: Optional[Path] = None,
                  dry_run: bool = False, export_json: bool = False) -> bool:
        """Parse a single MHD file.
        
        Args:
            file_path: Path to the MHD file
            output_dir: Directory for JSON output (if export_json is True)
            dry_run: If True, parse without database operations
            export_json: If True, export to JSON
            
        Returns:
            True if successful, False otherwise
        """
        if not file_path.exists():
            self.logger.error(f"File not found: {file_path}")
            return False
        
        self.logger.info(f"Parsing {file_path.name}...")
        start_time = time.time()
        
        try:
            with open(file_path, 'rb') as f:
                # Detect file format
                file_format = detect_file_format(f)
                
                if file_format in (FileFormat.TEXT_WITH_VERSION, FileFormat.TEXT_TSV):
                    # Text file
                    self.logger.debug(f"Detected text format: {file_format.value}")
                    result = parse_text_mhd(f)
                    
                    if export_json and output_dir:
                        json_path = output_dir / f"{file_path.stem}.json"
                        self.json_exporter.export_text_mhd(result, json_path)
                        self.logger.info(f"Exported to {json_path}")
                else:
                    # Binary file - determine type by filename
                    filename_lower = file_path.name.lower()
                    
                    if "i12" in filename_lower or "powers" in filename_lower:
                        result = parse_main_database(f)
                        if export_json and output_dir:
                            json_path = output_dir / f"{file_path.stem}_main.json"
                            self.json_exporter.export_main_database(result, json_path)
                            self.logger.info(f"Exported main database to {json_path}")
                    
                    elif "enh" in filename_lower:
                        result = parse_enhancement_database(f)
                        if export_json and output_dir:
                            json_path = output_dir / f"{file_path.stem}_enh.json"
                            self.json_exporter.export_enhancement_database(result, json_path)
                            self.logger.info(f"Exported enhancement database to {json_path}")
                    
                    elif "salvage" in filename_lower:
                        result = parse_salvage_database(f)
                        if export_json and output_dir:
                            json_path = output_dir / f"{file_path.stem}_salvage.json"
                            self.json_exporter.export_salvage_database(result, json_path)
                            self.logger.info(f"Exported salvage database to {json_path}")
                    
                    elif "recipe" in filename_lower:
                        result = parse_recipe_database(f)
                        if export_json and output_dir:
                            json_path = output_dir / f"{file_path.stem}_recipe.json"
                            self.json_exporter.export_recipe_database(result, json_path)
                            self.logger.info(f"Exported recipe database to {json_path}")
                    
                    else:
                        self.logger.warning(f"Unknown binary file type: {file_path.name}")
                        return False
            
            elapsed_time = time.time() - start_time
            self.logger.info(f"Successfully parsed {file_path.name} in {elapsed_time:.2f} seconds")
            
            if not dry_run:
                # TODO: Database import would go here
                self.logger.info("Database import not implemented (dry-run mode)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {str(e)}", exc_info=True)
            return False
    
    def parse_directory(self, directory: Path, pattern: str = "*.mhd",
                       output_dir: Optional[Path] = None,
                       dry_run: bool = False, export_json: bool = False) -> int:
        """Parse all MHD files in a directory.
        
        Args:
            directory: Directory containing MHD files
            pattern: Glob pattern for files
            output_dir: Directory for JSON output
            dry_run: If True, parse without database operations
            export_json: If True, export to JSON
            
        Returns:
            Number of successfully parsed files
        """
        if not directory.exists():
            self.logger.error(f"Directory not found: {directory}")
            return 0
        
        files = list(directory.glob(pattern))
        if not files:
            self.logger.warning(f"No files found matching pattern: {pattern}")
            return 0
        
        self.logger.info(f"Found {len(files)} files to parse")
        success_count = 0
        
        for i, file_path in enumerate(files, 1):
            self.logger.info(f"[{i}/{len(files)}] Processing {file_path.name}")
            if self.parse_file(file_path, output_dir, dry_run, export_json):
                success_count += 1
        
        self.logger.info(f"Successfully parsed {success_count}/{len(files)} files")
        return success_count
    
    def validate_file(self, file_path: Path) -> bool:
        """Validate a file without importing to database."""
        self.logger.info(f"Validating {file_path.name}...")
        
        try:
            with open(file_path, 'rb') as f:
                file_format = detect_file_format(f)
                
                if file_format in (FileFormat.TEXT_WITH_VERSION, FileFormat.TEXT_TSV):
                    result = parse_text_mhd(f)
                    self.logger.info(f"Valid text file with {len(result.data)} rows")
                else:
                    # Try to parse as each type
                    filename_lower = file_path.name.lower()
                    
                    if "i12" in filename_lower or "powers" in filename_lower:
                        result = parse_main_database(f)
                        self.logger.info(f"Valid main database: "
                                       f"{len(result.archetypes)} archetypes, "
                                       f"{len(result.powersets)} powersets, "
                                       f"{len(result.powers)} powers")
                    elif "enh" in filename_lower:
                        result = parse_enhancement_database(f)
                        self.logger.info(f"Valid enhancement database: "
                                       f"{len(result.enhancements)} enhancements, "
                                       f"{len(result.enhancement_sets)} sets")
                    elif "salvage" in filename_lower:
                        result = parse_salvage_database(f)
                        self.logger.info(f"Valid salvage database: "
                                       f"{len(result.salvage_items)} items")
                    elif "recipe" in filename_lower:
                        result = parse_recipe_database(f)
                        self.logger.info(f"Valid recipe database: "
                                       f"{len(result.recipes)} recipes")
                    else:
                        self.logger.warning(f"Unknown file type: {file_path.name}")
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Validation failed: {str(e)}")
            if hasattr(e, '__traceback__'):
                import traceback
                self.logger.debug(traceback.format_exc())
            return False


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Parse Mids Hero Designer data files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse a single file
  python -m app.mhd_parser.cli parse path/to/I12.mhd
  
  # Parse all files in a directory with JSON export
  python -m app.mhd_parser.cli parse path/to/data/ --export-json --output output/
  
  # Validate files without importing
  python -m app.mhd_parser.cli validate path/to/data/
  
  # Dry run with debug logging
  python -m app.mhd_parser.cli parse path/to/data/ --dry-run --log-level DEBUG
"""
    )
    
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Set logging level')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse MHD files')
    parse_parser.add_argument('path', type=Path,
                            help='File or directory to parse')
    parse_parser.add_argument('--pattern', default='*.mhd',
                            help='File pattern for directory parsing')
    parse_parser.add_argument('--dry-run', action='store_true',
                            help='Parse without database import')
    parse_parser.add_argument('--export-json', action='store_true',
                            help='Export parsed data to JSON')
    parse_parser.add_argument('--output', type=Path,
                            help='Output directory for JSON files')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', 
                                          help='Validate MHD files')
    validate_parser.add_argument('path', type=Path,
                               help='File or directory to validate')
    validate_parser.add_argument('--pattern', default='*.mhd',
                               help='File pattern for directory validation')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level)
    
    # Create CLI instance
    cli = MhdParserCLI()
    
    if args.command == 'parse':
        if args.path.is_file():
            success = cli.parse_file(args.path, args.output, 
                                   args.dry_run, args.export_json)
            sys.exit(0 if success else 1)
        else:
            count = cli.parse_directory(args.path, args.pattern, args.output,
                                      args.dry_run, args.export_json)
            sys.exit(0 if count > 0 else 1)
    
    elif args.command == 'validate':
        if args.path.is_file():
            success = cli.validate_file(args.path)
            sys.exit(0 if success else 1)
        else:
            files = list(args.path.glob(args.pattern))
            success_count = sum(1 for f in files if cli.validate_file(f))
            print(f"\nValidation complete: {success_count}/{len(files)} files valid")
            sys.exit(0 if success_count == len(files) else 1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()