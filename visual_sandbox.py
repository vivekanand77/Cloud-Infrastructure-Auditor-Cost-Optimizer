import os
os.system("")

import time
from rich import print
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.progress import Progress

console = Console(force_terminal=True)

with Progress() as progress:
    task = progress.add_task("[cyan]Scanning cloud resources...", total=100)
    while not progress.finished:
        time.sleep(0.03)
        progress.update(task, advance=1)

console.print("\n[bold green] Scan Complete![/bold green]\n")

table = Table(title="cloud resource monitor")
table.add_column("resource id", style="cyan", no_wrap=True)
table.add_column("type",        style="magenta")
table.add_column("region",        style="blue")
table.add_column("est. cost",        style="green")
table.add_column("status",        style="white")

def colour(status):
    if status =="idle":
        return Text(status, style="bold yellow")
    elif status =="unattached":
        return Text(status, style="bold red")
    else:
        return Text(status, style="bold green")        

table.add_row("res-001", "ec2 instance", "us-east-1", "$12.50", "running")
table.add_row("res-002", "s3 bucket", "ap-south-1", "$3.20", "idle")
table.add_row("res-003", "rds database", "eu-west-1", "45.00", "running")
table.add_row("res-004", "ebs voloume", "us-west-2", "$8.75", "unattached")
table.add_row("res-005", "lambda fn", "ap-south-1", "$0.90", "running")

console.print(table)