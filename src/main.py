"""
Main CLI application for the RAG system.
"""
import click
from pathlib import Path
import sys
import io

# Fix Windows console encoding for Romanian characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from loguru import logger

from .rag_system import RAGSystem
from .utils import setup_logging, load_config, load_env_file, print_header

console = Console()


@click.group()
@click.option('--config', default='./config/config.yaml', help='Path to config file')
@click.option('--log-level', default='INFO', help='Logging level')
@click.option('--log-file', default=None, help='Log file path')
@click.pass_context
def cli(ctx, config, log_level, log_file):
    """
    RAG System for Energy Sector Data Analysis.

    Sistem de cautare si analiza a datelor despre furnizori de energie electrica.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)

    # Setup logging
    if log_file is None:
        log_file = './logs/rag_system.log'

    setup_logging(log_level=log_level, log_file=log_file)

    # Load environment variables
    load_env_file()

    # Store config path in context
    ctx.obj['config_path'] = config


@cli.command()
@click.option('--input-dir', default='./data/input', help='Directory with Excel files')
@click.option('--embeddings-dir', default='./embeddings', help='Directory for embeddings')
@click.option('--prompts-dir', default='./prompts', help='Directory with prompts')
@click.option('--embedding-model', default=None, help='Embedding model name')
@click.option('--force', is_flag=True, help='Force reindexing')
@click.pass_context
def index(ctx, input_dir, embeddings_dir, prompts_dir, embedding_model, force):
    """
    Index Excel documents for search.

    Incarca si indexeaza toate fisierele Excel din directorul specificat.
    """
    console.print("\n[bold blue]Indexing Documents[/bold blue]\n")

    try:
        # Initialize RAG system
        rag = RAGSystem(
            input_dir=input_dir,
            prompts_dir=prompts_dir,
            embeddings_dir=embeddings_dir,
            config_path=ctx.obj['config_path']
        )

        # Initialize components
        with console.status("[bold green]Initializing components..."):
            rag.initialize_components(embedding_model=embedding_model)

        console.print("[green]✓[/green] Components initialized\n")

        # Index documents
        console.print("[yellow]Loading and indexing documents...[/yellow]")
        num_docs = rag.index_documents(force_reindex=force)

        console.print(f"\n[green]✓[/green] Successfully indexed [bold]{num_docs}[/bold] documents")

        # Show statistics
        stats = rag.get_statistics()

        table = Table(title="Index Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        for key, value in stats.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    table.add_row(f"{key}.{sub_key}", str(sub_value))
            else:
                table.add_row(key, str(value))

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}")
        logger.exception("Indexing failed")
        sys.exit(1)


@cli.command()
@click.option('--query', '-q', required=True, help='Search query')
@click.option('--embeddings-dir', default='./embeddings', help='Directory with embeddings')
@click.option('--prompts-dir', default='./prompts', help='Directory with prompts')
@click.option('--top-k', default=5, help='Number of results to return')
@click.option('--no-llm', is_flag=True, help='Skip LLM generation, show only search results')
@click.pass_context
def search(ctx, query, embeddings_dir, prompts_dir, top_k, no_llm):
    """
    Search for documents matching a query.

    Cauta documente relevante pentru o intrebare data.
    """
    console.print(f"\n[bold blue]Searching:[/bold blue] {query}\n")

    try:
        # Initialize RAG system
        rag = RAGSystem(
            prompts_dir=prompts_dir,
            embeddings_dir=embeddings_dir,
            config_path=ctx.obj['config_path']
        )

        # Initialize components
        with console.status("[bold green]Loading system..."):
            rag.initialize_components()
            rag.load_index()

        # Perform search
        if no_llm:
            results = rag.search(query, top_k=top_k)

            # Display results
            for i, result in enumerate(results, 1):
                metadata = result["metadata"]
                score = result.get("score", 0)

                console.print(f"\n[bold cyan]{i}. {metadata.get('client_name', 'N/A')}[/bold cyan] (Score: {score:.3f})")

                if metadata.get("source_type"):
                    console.print(f"   [green]Sursa:[/green] {metadata['source_type']}")

                if metadata.get("power_installed"):
                    console.print(f"   [green]Putere:[/green] {metadata['power_installed']} MW")

                if metadata.get("address"):
                    console.print(f"   [green]Locatie:[/green] {metadata['address']}")
        else:
            # Full RAG query with LLM
            answer = rag.query(query, top_k=top_k)

            console.print("\n[bold green]Answer:[/bold green]\n")
            console.print(answer)

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}")
        logger.exception("Search failed")
        sys.exit(1)


@cli.command()
@click.option('--embeddings-dir', default='./embeddings', help='Directory with embeddings')
@click.option('--prompts-dir', default='./prompts', help='Directory with prompts')
@click.option('--top-k', default=5, help='Number of results per query')
@click.pass_context
def interactive(ctx, embeddings_dir, prompts_dir, top_k):
    """
    Start interactive search session.

    Porneste o sesiune interactiva de cautare.
    """
    try:
        # Initialize RAG system
        rag = RAGSystem(
            prompts_dir=prompts_dir,
            embeddings_dir=embeddings_dir,
            config_path=ctx.obj['config_path']
        )

        # Initialize components
        with console.status("[bold green]Loading system..."):
            rag.initialize_components()
            rag.load_index()

        console.print("[green]✓[/green] System ready\n")

        # Start interactive session
        rag.interactive_search()

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}")
        logger.exception("Interactive session failed")
        sys.exit(1)


@cli.command()
@click.option('--query', '-q', required=True, help='Search query for report')
@click.option('--output', '-o', required=True, help='Output file path (timestamp will be added automatically)')
@click.option('--embeddings-dir', default='./embeddings', help='Directory with embeddings')
@click.option('--prompts-dir', default='./prompts', help='Directory with prompts')
@click.option('--format', type=click.Choice(['markdown', 'md']), default='markdown', help='Output format')
@click.option('--include-summary', is_flag=True, help='Include LLM-generated summary')
@click.option('--no-timestamp', is_flag=True, help='Disable automatic timestamp in filename')
@click.pass_context
def generate_report(ctx, query, output, embeddings_dir, prompts_dir, format, include_summary, no_timestamp):
    """
    Generate a comprehensive report.

    Genereaza un raport detaliat pentru o cautare.
    """
    from datetime import datetime

    # Add timestamp to filename unless disabled
    if not no_timestamp:
        output_path = Path(output)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Insert timestamp before extension
        new_name = f"{timestamp}_{output_path.stem}{output_path.suffix}"
        output = str(output_path.parent / new_name)

    console.print(f"\n[bold blue]Generating Report[/bold blue]\n")
    console.print(f"Query: {query}")
    console.print(f"Output: {output}\n")

    try:
        # Initialize RAG system
        rag = RAGSystem(
            prompts_dir=prompts_dir,
            embeddings_dir=embeddings_dir,
            config_path=ctx.obj['config_path']
        )

        # Initialize components
        with console.status("[bold green]Loading system..."):
            rag.initialize_components()
            rag.load_index()

        # Generate report
        with console.status("[bold yellow]Generating report..."):
            report = rag.generate_report(
                query,
                output_path=output,
                include_summary=include_summary
            )

        console.print(f"\n[green]✓[/green] Report saved to: {output}")

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}")
        logger.exception("Report generation failed")
        sys.exit(1)


@cli.command()
@click.option('--embeddings-dir', default='./embeddings', help='Directory with embeddings')
@click.pass_context
def stats(ctx, embeddings_dir):
    """
    Show system statistics.

    Afiseaza statistici despre sistemul RAG.
    """
    console.print("\n[bold blue]System Statistics[/bold blue]\n")

    try:
        # Initialize RAG system
        rag = RAGSystem(
            embeddings_dir=embeddings_dir,
            config_path=ctx.obj['config_path']
        )

        # Initialize components
        with console.status("[bold green]Loading system..."):
            rag.initialize_components()
            rag.load_index()

        # Get statistics
        statistics = rag.get_statistics()

        # Display in table
        table = Table(title="RAG System Statistics")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")

        for key, value in statistics.items():
            if isinstance(value, dict):
                # Add header for nested dict
                table.add_row(f"[bold]{key}[/bold]", "")
                for sub_key, sub_value in value.items():
                    table.add_row(f"  {sub_key}", str(sub_value))
            else:
                table.add_row(key, str(value))

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}")
        logger.exception("Stats retrieval failed")
        sys.exit(1)


@cli.command()
@click.option('--input-dir', default='./data/input', help='Directory with Excel files')
@click.option('--output', '-o', help='Output file path (JSON or Parquet)')
@click.pass_context
def export_data(ctx, input_dir, output):
    """
    Export loaded data to JSON or Parquet.

    Exporta datele incarcate in format JSON sau Parquet.
    """
    console.print("\n[bold blue]Exporting Data[/bold blue]\n")

    try:
        from .data_loader import ExcelDataLoader

        # Load config
        config = load_config(ctx.obj['config_path'])
        column_mappings = config.get("excel", {}).get("column_mappings")

        # Initialize loader
        loader = ExcelDataLoader(input_dir, column_mappings=column_mappings)

        # Load data
        with console.status("[bold green]Loading Excel files..."):
            records = loader.load_all_files()

        console.print(f"[green]✓[/green] Loaded {len(records)} records\n")

        # Export
        if output:
            ext = Path(output).suffix.lower()

            if ext == '.json':
                loader.export_to_json(output)
            elif ext == '.parquet':
                loader.export_to_parquet(output)
            else:
                console.print("[red]Unsupported format. Use .json or .parquet[/red]")
                sys.exit(1)

            console.print(f"[green]✓[/green] Data exported to: {output}")
        else:
            # Show sample data
            import pandas as pd
            df = loader.to_dataframe()
            console.print(df.head(10))

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}")
        logger.exception("Export failed")
        sys.exit(1)


@cli.command()
def version():
    """Show version information."""
    from . import __version__
    console.print(f"\n[bold blue]RAG System for Energy Data[/bold blue]")
    console.print(f"Version: {__version__}\n")


if __name__ == '__main__':
    cli(obj={})
