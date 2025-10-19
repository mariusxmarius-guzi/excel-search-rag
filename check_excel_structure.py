"""
Script pentru verificarea structurii fișierelor Excel.
Arată ce sheets, coloane și câte rânduri sunt în fiecare fișier.
"""
import sys
import io
from pathlib import Path
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

console = Console()


def check_excel_file(file_path: Path):
    """Verifică structura unui fișier Excel."""
    try:
        excel = pd.ExcelFile(file_path)

        # Panel pentru fișier
        console.print(Panel(
            f"[bold cyan]{file_path.name}[/bold cyan]",
            title="📊 Excel File",
            border_style="cyan"
        ))

        # Tabel pentru sheets
        table = Table(title=f"Sheets & Columns", show_lines=True)
        table.add_column("Sheet Name", style="cyan", no_wrap=False)
        table.add_column("Rows", style="green", justify="right")
        table.add_column("Columns", style="yellow", no_wrap=False)

        total_sheets = 0
        total_rows = 0

        for sheet_name in excel.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)

            # Format coloane
            if df.empty:
                columns_str = "[red]EMPTY[/red]"
                rows_str = "0"
            else:
                columns = list(df.columns)[:10]  # Primele 10 coloane
                if len(df.columns) > 10:
                    columns_str = ", ".join(columns) + f" ... (+{len(df.columns)-10} more)"
                else:
                    columns_str = ", ".join(columns)
                rows_str = str(len(df))

            table.add_row(sheet_name, rows_str, columns_str)
            total_sheets += 1
            total_rows += len(df)

        console.print(table)
        console.print(f"[bold]Summary:[/bold] {total_sheets} sheets, {total_rows} total rows\n")

        return True

    except Exception as e:
        console.print(f"[red]❌ Error:[/red] {e}\n")
        return False


def main():
    """Main function."""
    console.print("\n[bold blue]Excel Structure Checker[/bold blue]\n")

    # Find all Excel files
    data_dir = Path("data/input")

    if not data_dir.exists():
        console.print(f"[red]❌ Directory not found:[/red] {data_dir}")
        return

    excel_files = list(data_dir.glob("*.xlsx")) + list(data_dir.glob("*.xls"))

    if not excel_files:
        console.print(f"[yellow]⚠️  No Excel files found in:[/yellow] {data_dir}")
        return

    console.print(f"[green]Found {len(excel_files)} Excel files[/green]\n")

    # Check each file
    success_count = 0
    for file_path in sorted(excel_files):
        if check_excel_file(file_path):
            success_count += 1

    # Summary
    console.print(Panel(
        f"[bold green]✓[/bold green] Successfully checked {success_count}/{len(excel_files)} files",
        title="Summary",
        border_style="green"
    ))


if __name__ == "__main__":
    main()
