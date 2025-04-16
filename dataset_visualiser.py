import os
import time
from itertools import cycle
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.style import Style
from rich.live import Live
import pandas as pd

def visualize_dataset(file_path):
    console = Console()

    # Check if the file exists
    if os.path.exists(file_path):
        # Load the dataset
        df = pd.read_csv(file_path)
        
        # Create a panel for the dataset info
        info_panel = Panel.fit(
            f"[bold]Dataset loaded successfully[/]\n\n"
            f"• [bold]Location:[/] {file_path}\n"
            f"• [bold]Shape:[/] {df.shape[0]} rows × {df.shape[1]} columns\n"
            f"• [bold]Memory usage:[/] {df.memory_usage().sum()/1024:.2f} KB\n"
            f"• [bold]Tip:[/] Use horizontal scrolling (Shift+Wheel) to view all columns",
            title="[bold green]Dataset Information[/]",
            border_style="bright_blue"
        )
        
        console.print(info_panel)
        
        # Function to create table with optional columns
        def create_table(columns_to_show=None, max_width=120):
            if columns_to_show is None:
                columns_to_show = df.columns.tolist()
            
            table = Table(
                title=f"\n[bold]First 10 Rows[/] (of {df.shape[0]}) | Showing {len(columns_to_show)}/{len(df.columns)} columns",
                width=min(max_width, console.width),
                show_header=True,
                header_style="bold cyan",
                border_style="cyan",
                style=None,
                row_styles=["", "grey37"],
                highlight=True,
                show_lines=False,
                expand=True
            )
            
            for column in columns_to_show:
                table.add_column(
                    column, 
                    header_style=Style(color="cyan", bold=True),
                    style=None,
                    justify="left",
                    overflow="ellipsis",
                    min_width=15,
                    max_width=30
                )
            
            color_cycle = cycle(["green", "yellow"])
            for _, row in df.head(10).iterrows():
                row_values = [str(row[col]) if col in row else "" for col in columns_to_show]
                table.add_row(*row_values, style=next(color_cycle))
            
            return table
        
        # Live rendering — rotate through all columns 5 at a time
        chunk_size = 5
        all_columns = df.columns.tolist()
        
        with Live(console=console, refresh_per_second=0.5) as live:
            for start in range(0, len(all_columns), chunk_size):
                subset = all_columns[start:start+chunk_size]
                live.update(create_table(subset))
                time.sleep(5)

    else:
        error_panel = Panel.fit(
            f"[bold red]File not found[/]\n\n"
            f"Path: [underline]{file_path}[/]\n\n"
            "Please check:\n"
            "1. If the file exists\n"
            "2. If the path is correct\n"
            "3. Your current working directory",
            title="[bold red]Error[/]",
            border_style="red"
        )
        console.print(error_panel)
        console.print(f"\nCurrent working directory: [underline]{os.getcwd()}[/]")