"""CLI interface for JSON import module."""

import asyncio
import json
import logging
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from app.database import get_async_session
from .importers import (
    import_archetypes,
    import_enhancements,
    import_powers,
    import_powersets,
    import_from_directory,
)

console = Console()
logger = logging.getLogger(__name__)


@click.group()
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    help="Set logging level",
)
def cli(log_level: str):
    """JSON Import CLI for City of Heroes data.

    This replaces the deprecated MHD binary import functionality.
    """
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


@cli.command()
@click.argument("directory", type=click.Path(exists=True, path_type=Path))
@click.option("--dry-run", is_flag=True, help="Validate without importing")
def import_all(directory: Path, dry_run: bool):
    """Import all JSON data from a directory.

    Expected files:
    - archetypes.json
    - powersets.json
    - powers.json
    - enhancements.json
    """
    console.print(f"[bold blue]Importing data from {directory}[/bold blue]")

    if dry_run:
        console.print("[yellow]DRY RUN: No data will be imported[/yellow]")
        # TODO: Implement validation-only mode
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Importing data...", total=None)

        try:
            stats = asyncio.run(import_from_directory(directory))

            # Display results
            table = Table(title="Import Results")
            table.add_column("Data Type", style="cyan")
            table.add_column("Total", style="white")
            table.add_column("Imported", style="green")
            table.add_column("Failed", style="red")

            for data_type, type_stats in stats.items():
                table.add_row(
                    data_type.capitalize(),
                    str(type_stats["total"]),
                    str(type_stats["imported"]),
                    str(type_stats["failed"]),
                )

            console.print(table)

            # Show errors if any
            for data_type, type_stats in stats.items():
                if type_stats.get("errors"):
                    console.print(
                        f"\n[red]Errors in {data_type}:[/red]", style="bold"
                    )
                    for error in type_stats["errors"][:5]:  # Show first 5 errors
                        console.print(
                            f"  - Record {error['index']}: {error['error']}"
                        )
                    if len(type_stats["errors"]) > 5:
                        console.print(
                            f"  ... and {len(type_stats['errors']) - 5} more"
                        )

        except Exception as e:
            console.print(f"[red]Import failed: {e}[/red]")
            raise


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--type",
    "data_type",
    required=True,
    type=click.Choice(["archetype", "powerset", "power", "enhancement"]),
    help="Type of data to import",
)
@click.option("--batch-size", default=1000, help="Batch size for large imports")
def import_file(file: Path, data_type: str, batch_size: int):
    """Import a specific JSON file."""
    console.print(f"[bold blue]Importing {data_type} data from {file}[/bold blue]")

    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Ensure data is a list
        if not isinstance(data, list):
            data = [data]

        async def run_import():
            async for session in get_async_session():
                try:
                    if data_type == "archetype":
                        return await import_archetypes(session, data)
                    elif data_type == "powerset":
                        return await import_powersets(session, data)
                    elif data_type == "power":
                        return await import_powers(session, data)
                    elif data_type == "enhancement":
                        return await import_enhancements(session, data)
                finally:
                    await session.close()

        stats = asyncio.run(run_import())

        # Display results
        console.print(f"\n[green]Import completed![/green]")
        console.print(f"Total records: {stats['total']}")
        console.print(f"Successfully imported: {stats['imported']}")
        console.print(f"Failed: {stats['failed']}")

        if stats.get("errors"):
            console.print(f"\n[red]Errors:[/red]")
            for error in stats["errors"][:10]:  # Show first 10 errors
                console.print(f"  - Record {error['index']}: {error['error']}")
            if len(stats["errors"]) > 10:
                console.print(f"  ... and {len(stats['errors']) - 10} more")

    except Exception as e:
        console.print(f"[red]Import failed: {e}[/red]")
        raise


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--schema",
    required=True,
    type=click.Choice(["archetype", "powerset", "power", "enhancement"]),
    help="Schema to validate against",
)
def validate(file: Path, schema: str):
    """Validate a JSON file against a schema."""
    from .validators import JsonSchemaValidator

    console.print(f"[bold blue]Validating {file} against {schema} schema[/bold blue]")

    validator = JsonSchemaValidator()

    try:
        validated = validator.validate_file(file, schema)
        console.print(
            f"[green]✓ Successfully validated {len(validated)} records[/green]"
        )
    except Exception as e:
        console.print(f"[red]✗ Validation failed: {e}[/red]")
        raise


@cli.command()
def show_schemas():
    """Display available JSON schemas."""
    from .validators import (
        ArchetypeSchema,
        EnhancementSchema,
        PowerSchema,
        PowersetSchema,
    )

    schemas = {
        "Power": PowerSchema,
        "Powerset": PowersetSchema,
        "Archetype": ArchetypeSchema,
        "Enhancement": EnhancementSchema,
    }

    for name, schema_class in schemas.items():
        console.print(f"\n[bold cyan]{name} Schema:[/bold cyan]")
        console.print(schema_class.schema_json(indent=2))


if __name__ == "__main__":
    cli()