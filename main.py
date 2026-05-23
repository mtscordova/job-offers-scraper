import click
from datetime import datetime, timezone, timedelta
from tabulate import tabulate
import db
from config import is_spain_or_remote, matches_keywords, MAX_AGE_DAYS
from scrapers import jobfluent, relocate, landing_jobs, greenhouse, lever

SOURCES = {
    "jobfluent": jobfluent.scrape,
    "relocate": relocate.scrape,
    "landing_jobs": landing_jobs.scrape,
    "greenhouse": greenhouse.scrape,
    "lever": lever.scrape,
}


def _is_too_old(posted_at: str | None, max_days: int) -> bool:
    if not posted_at:
        return False  # sin fecha, no descartamos
    try:
        dt = datetime.fromisoformat(posted_at.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).days > max_days
    except ValueError:
        return False


@click.group()
def cli():
    pass


@cli.command()
@click.option("--source", type=click.Choice(list(SOURCES)), default=None, help="Scrape only this source.")
@click.option("--days", default=MAX_AGE_DAYS, show_default=True, help="Descartar ofertas con más de N días.")
def scrape(source, days):
    """Scrape job offers and save new ones to the database."""
    db.init_db()
    removed = db.purge_old_jobs(days)
    if removed:
        click.echo(f"Removed {removed} expired jobs (older than {days} days).")
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
            if not matches_keywords(job.title):
                skipped += 1
                continue
            if not is_spain_or_remote(job.location or "", job.remote):
                skipped += 1
                continue
            if _is_too_old(job.posted_at, days):
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
@click.option("--days", default=None, type=int, help="Mostrar solo ofertas scrapeadas en los últimos N días.")
def list_jobs(source, limit, days):
    """List saved job offers."""
    db.init_db()
    jobs = db.fetch_jobs(source=source, limit=limit, days=days)
    if not jobs:
        click.echo("No jobs found.")
        return

    rows = [
        [
            j["id"],
            j["title"][:50],
            j["company"][:22],
            j["location"][:18],
            j["source"],
            "yes" if j["remote"] else "no",
            (j["posted_at"] or j["scraped_at"] or "")[:10],
        ]
        for j in jobs
    ]
    click.echo(tabulate(rows, headers=["ID", "Title", "Company", "Location", "Source", "Remote", "Date"]))
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
