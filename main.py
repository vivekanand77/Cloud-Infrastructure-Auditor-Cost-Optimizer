import typer
from typing import Optional

app = typer.Typer(help="Cloud Infrastructure Auditor & Cost Optimizer")

@app.command()
def scan(
    service: str = typer.Argument(..., help="AWS Service to scan (e.g., ec2, cloudwatch)"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS CLI profile name"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region")
):
    """
    Scan AWS services for cost optimization opportunities.
    """
    typer.echo(f"Scanning {service}...")
 
 
    # Authentication and routing logic will go here
@app.command()
def clean(
    service: str = typer.Argument(...,help = 'AWS Service to Report'),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS CLI profile name"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region")
):
    """
    Remove unused Resources for a given service
    """
    typer.echo(f"Cleaning  {service}")
@app.command()
def report(
    service: str = typer.Argument(...,help = 'AWS Service to Report'),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS CLI profile name"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region")
):
    """
    Generate a waste report on AWS services 
    """
    typer.echo(f"Generating Report on {service}")
@app.command()
def config(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS CLI profile name"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region")
):
    """Saving default profile and region for all commands"""
    typer.echo("Saving Config...")
if __name__ == "__main__":
    app()
