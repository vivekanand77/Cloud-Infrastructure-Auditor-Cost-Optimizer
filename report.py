from rich.console import Console
from rich.table import Table
from rich import box
from aggregator.aggregator import aggregate_data

# ── Mock Data (Week 2 wala) ──
mock_ebs = [{
    "volume_id": "vol-0abc123",
    "size_gb": 100,
    "volume_type": "gp2",
    "region": "us-east-1",
    "state": "available",
    "attached_instance_id": None
}]

mock_eip = [{
    "allocation_id": "eipalloc-0xyz",
    "public_ip": "3.4.5.6",
    "region": "us-east-1",
    "associated": False,
    "instance_id": None
}]

mock_cpu = [
    {
        "instance_id": "i-aaa",
        "region": "us-east-1",
        "avg_cpu_percent": 2.88,
        "is_flagged": True,
        "account_id": "123456789012",
        "flagged_at": "2026-06-28T12:00:00+00:00"
    },
    {
        "instance_id": "i-bbb",
        "region": "us-east-1",
        "avg_cpu_percent": 3.1,
        "is_flagged": True,
        "account_id": "123456789012",
        "flagged_at": "2026-06-28T12:00:00+00:00"
    }
]


def build_report(data: list) -> None:
    console = Console()

    table = Table(
        title="🔍 Cloud Infrastructure Audit Report",
        box=box.DOUBLE_EDGE,
        show_header=True,
        header_style="bold cyan"
    )

    table.add_column("Resource ID", style="white", no_wrap=True)
    table.add_column("Type", style="yellow")
    table.add_column("Region", style="blue")
    table.add_column("Status", style="magenta")
    table.add_column("Metric Value", justify="right")
    table.add_column("Waste $", justify="right", style="red")

    total_waste = 0.0

    for record in data:
        rtype = record["resource_type"]
        metric = record["metric_value"]
        waste = record["estimated_waste_usd"]
        total_waste += waste

        # Metric display
        if rtype == "EBS":
            metric_str = f"{metric:.0f} GB"
        elif rtype == "EC2-CPU":
            metric_str = f"{metric:.2f}%"
        else:
            metric_str = "-"

        # Status color
        status = record["status"]
        status_str = f"[red]{status}[/red]" if status in ["idle", "underutilized"] else f"[green]{status}[/green]"

        table.add_row(
            record["resource_id"],
            rtype,
            record["region"],
            status_str,
            metric_str,
            f"${waste:.2f}"
        )

    console.print(table)
    console.print(f"\n[bold]Total Resources:[/bold] {len(data)}   [bold red]Total Estimated Waste: ${total_waste:.2f}[/bold red]\n")


if __name__ == "__main__":
    data = aggregate_data(mock_ebs, mock_eip, mock_cpu)
    build_report(data)