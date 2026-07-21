import typer
from typing import Optional

from utils.session_manager import get_session
from scanners.asset_retrieval import get_unattached_ebs_volumes, get_unassociated_elastic_ips
from cloudwatch_metrics import get_low_cpu_instances
from aggregator.aggregator import aggregate_data
from report import build_report

app = typer.Typer(help="Cloud Infrastructure Auditor & Cost Optimizer")

DEFAULT_REGION = "us-east-1"


@app.command()
def scan(
    service: str = typer.Argument(..., help="AWS service to scan: ebs | eip | ec2 | all"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS CLI profile name"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region (default: us-east-1)"),
):
    """Scan AWS resources and display a cost waste report."""
    r = region or DEFAULT_REGION
    session = get_session(profile_name=profile)

    typer.echo(f"🔍  Scanning [{service.upper()}] in {r} ...")

    ebs_data, eip_data, cpu_data = [], [], []

    if service in ("ebs", "all"):
        ebs_data = get_unattached_ebs_volumes(session=session, region=r)
        typer.echo(f"   EBS  — {len(ebs_data)} unattached volume(s) found")

    if service in ("eip", "all"):
        eip_data = get_unassociated_elastic_ips(session=session, region=r)
        typer.echo(f"   EIP  — {len(eip_data)} unassociated IP(s) found")

    if service in ("ec2", "all"):
        cpu_data = get_low_cpu_instances(region=r, boto_session=session)
        typer.echo(f"   EC2  — {len(cpu_data)} underutilised instance(s) found")

    combined = aggregate_data(ebs_data, eip_data, cpu_data)
    build_report(combined)


@app.command()
def report(
    service: str = typer.Argument(..., help="AWS service to report on: ebs | eip | ec2 | all"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS CLI profile name"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
):
    """Generate a waste report (alias for scan — does not modify anything)."""
    # report is intentionally the same as scan — it reads, never writes
    r = region or DEFAULT_REGION
    session = get_session(profile_name=profile)

    ebs_data = get_unattached_ebs_volumes(session=session, region=r) if service in ("ebs", "all") else []
    eip_data = get_unassociated_elastic_ips(session=session, region=r) if service in ("eip", "all") else []
    cpu_data = get_low_cpu_instances(region=r, boto_session=session) if service in ("ec2", "all") else []

    build_report(aggregate_data(ebs_data, eip_data, cpu_data))


@app.command()
def clean(
    service: str = typer.Argument(..., help="AWS service to clean"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS CLI profile name"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
):
    """Remove unused resources (run scan first to preview what will be deleted)."""
    typer.echo("⚠️  clean is not yet implemented — run `scan` first to review waste.")
    typer.echo("    Destructive operations will be added once scan output is validated.")


@app.command()
def config(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS CLI profile name"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
):
    """Save a default profile and region so you don't have to type them every time."""
    import json, pathlib
    cfg_path = pathlib.Path.home() / ".cosmo_audit_config"
    current = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}

    if profile:
        current["profile"] = profile
    if region:
        current["region"] = region

    cfg_path.write_text(json.dumps(current, indent=2))
    typer.echo(f"✅  Config saved to {cfg_path}")
    typer.echo(f"    profile = {current.get('profile', '(not set)')}")
    typer.echo(f"    region  = {current.get('region', '(not set)')}")


if __name__ == "__main__":
    app()

