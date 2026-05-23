import click
from tabulate import tabulate
import db
from config import is_spain_or_remote
from scrapers import jobfluent, relocate, landing_jobs, greenhouse, lever

SOURCES = {
    "jobfluent": jobfluent.scrape,
    "relocate": relocate.scrape,
    "landing_jobs": landing_jobs.scrape,
    "greenhouse": greenhouse.scrape,
    "lever": lever.scrape,
}


@click.group()
def cli():
    pass


@cli.command()
@click.option("--source", type=click.Choice(list(SOURCES)), default=None, help="Scrape only this source.")
def scrape(source):
    """Scrape job offers and save new ones to the database."""
    db.init_db()
    targets = {source: SOURCES[source]} if source else SOURCES

    for name, scrape_fn in targets.items():
        click.echo(f"Scraping {name}...")
        try:
            jobs = scrape_fn()
        except Exception as e:
            click.echo(f"  ERROR: {e}")
            continue

        new, dupes, skipped = 0, 0, 0
        for job in jobs:
            if not is_spain_or_remote(job.location or "", job.remote):
                skipped += 1
                continue
            if db.save_job(job.to_dict()):
                new += 1
            else:
                dupes += 1

        click.echo(f"  {new} new  |  {dupes} already in DB  |  {skipped} filtered out  (fetched: {len(jobs)})")


@cli.command("list")
@click.option("--source", type=click.Choice(list(SOURCES)), default=None)
@click.option("--limit", default=50, show_default=True)
def list_jobs(source, limit):
    """List saved job offers."""
    db.init_db()
    jobs = db.fetch_jobs(source=source, limit=limit)
    if not jobs:
        click.echo("No jobs found.")
        return

    rows = [
        [j["id"], j["title"][:55], j["company"][:25], j["location"][:20], j["source"], "yes" if j["remote"] else "no"]
        for j in jobs
    ]
    click.echo(tabulate(rows, headers=["ID", "Title", "Company", "Location", "Source", "Remote"]))
    click.echo(f"\n{len(jobs)} jobs shown.")


@cli.command()
def stats():
    """Show job counts per source."""
    db.init_db()
    rows = db.fetch_stats()
    if not rows:
        click.echo("No data yet. Run: python main.py scrape")
        return
    click.echo(tabulate([[r["source"], r["total"]] for r in rows], headers=["Source", "Total"]))


if __name__ == "__main__":
    cli()
