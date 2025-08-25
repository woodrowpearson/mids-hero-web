#!/usr/bin/env python3
"""CLI script for importing I12 power data using the streaming parser."""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import after path setup to avoid E402
from app.data_import import I12StreamingParser  # noqa: E402
from app.services.power_cache import get_power_cache  # noqa: E402


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("i12_import.log"),
        ],
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Import I12 power data using streaming parser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import from JSON file with default settings
  python import_i12_data.py /path/to/i12_data.json

  # Import with custom batch size and memory limit
  python import_i12_data.py /path/to/i12_data.json --batch-size 500 --memory-limit 0.5

  # Resume import from specific record
  python import_i12_data.py /path/to/i12_data.json --resume-from 50000

  # Test run with validation only (no database writes)
  python import_i12_data.py /path/to/i12_data.json --validate-only
        """,
    )

    parser.add_argument("json_file", type=Path, help="Path to I12 JSON data file")

    parser.add_argument(
        "--database-url",
        type=str,
        default=os.getenv("DATABASE_URL", "postgresql://localhost/mids_web"),
        help="Database connection URL (default: from DATABASE_URL env var)",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Number of records to process in each batch (default: 1000)",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=5000,
        help="Number of records to read from file at once (default: 5000)",
    )

    parser.add_argument(
        "--memory-limit",
        type=float,
        default=1.0,
        help="Memory limit in GB before forcing garbage collection (default: 1.0)",
    )

    parser.add_argument(
        "--resume-from",
        type=int,
        default=0,
        help="Record number to resume import from (default: 0)",
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate data without importing to database",
    )

    parser.add_argument(
        "--clear-cache", action="store_true", help="Clear power cache before import"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set up logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Validate input file
    if not args.json_file.exists():
        logger.error(f"Input file does not exist: {args.json_file}")
        sys.exit(1)

    if not args.json_file.suffix.lower() == ".json":
        logger.error(f"Input file must be a JSON file: {args.json_file}")
        sys.exit(1)

    logger.info(f"Starting I12 data import from {args.json_file}")
    logger.info(f"Database URL: {args.database_url}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info(f"Chunk size: {args.chunk_size}")
    logger.info(f"Memory limit: {args.memory_limit}GB")

    if args.resume_from > 0:
        logger.info(f"Resuming from record {args.resume_from}")

    if args.validate_only:
        logger.info("Validation mode: No data will be written to database")

    # Clear cache if requested
    if args.clear_cache:
        logger.info("Clearing power cache")
        cache = get_power_cache()
        cache.clear_all_cache()

    # Create parser
    parser = I12StreamingParser(
        database_url=args.database_url,
        batch_size=args.batch_size,
        chunk_size=args.chunk_size,
        memory_limit_gb=args.memory_limit,
    )

    # Progress callback
    def progress_callback(processed: int, total: int, percentage: float):
        if processed % 10000 == 0 or percentage == 100.0:
            logger.info(f"Progress: {processed}/{total} ({percentage:.1f}%)")

    try:
        if args.validate_only:
            logger.info("Starting validation...")
            # TODO: Implement validation-only mode
            logger.warning("Validation-only mode not yet implemented")
            sys.exit(1)
        else:
            logger.info("Starting import...")
            parser.import_data(
                file_path=args.json_file,
                resume_from=args.resume_from,
                progress_callback=progress_callback,
            )

        # Display final statistics
        logger.info("Import completed successfully!")
        logger.info(f"Records processed: {parser.processed_count}")
        logger.info(f"Records imported: {parser.imported_count}")
        logger.info(f"Errors encountered: {parser.error_count}")

        if parser.errors:
            logger.warning("Errors details (first 10):")
            for i, error in enumerate(parser.errors[:10]):
                logger.warning(
                    f"  {i + 1}. Record {error['record_index']}: {error['error']}"
                )

        # Cache statistics
        cache = get_power_cache()
        cache_stats = cache.get_cache_stats()
        logger.info(f"Cache statistics: {cache_stats}")

        if parser.error_count > 0:
            logger.warning(f"Import completed with {parser.error_count} errors")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Import interrupted by user")
        logger.info(f"Progress: {parser.processed_count} records processed")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Import failed with error: {e}")
        logger.error(f"Progress: {parser.processed_count} records processed")
        sys.exit(1)


if __name__ == "__main__":
    main()
