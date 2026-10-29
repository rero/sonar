# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Organisations CLI commands."""

import click
from flask.cli import with_appcontext
from invenio_db import db
from marshmallow import ValidationError

from .api import OrganisationRecord
from .marshmallow.json import ThemeSchemaV1


@click.group()
def organisations():
    """Organisations commands."""


@organisations.group()
def theme():
    """Organisation theme commands, applied without restarting the application."""


def get_organisation(code):
    """Return the organisation with the given code or abort."""
    if organisation := OrganisationRecord.get_record_by_pid(code):
        return organisation
    click.secho(f"Organisation {code} does not exist.", fg="red")
    raise click.Abort()


@theme.command("set")
@click.argument("code")
@click.option("--primary", help="Primary color, e.g. #D7182A.")
@click.option("--secondary", help="Secondary color, e.g. #EB8B94.")
@click.option(
    "--css",
    type=click.File(encoding="utf-8"),
    help="CSS file applied over the compiled theme, or - to read it from stdin.",
)
@with_appcontext
def set_theme(code, primary, secondary, css):
    """Set the theme of a dedicated organisation.

    Only the given values are changed, the others are kept.
    """
    values = {"primaryColor": primary, "secondaryColor": secondary, "css": css.read() if css else None}
    values = {key: value for key, value in values.items() if value is not None}
    if not values:
        click.secho("Nothing to set.", fg="red")
        raise click.Abort()

    organisation = get_organisation(code)
    if not organisation.get("isDedicated"):
        click.secho(f"Organisation {code} is not dedicated.", fg="red")
        raise click.Abort()

    try:
        organisation["theme"] = ThemeSchemaV1().load({**organisation.get("theme", {}), **values})
    except ValidationError as error:
        click.secho(f"Invalid theme: {error.messages}", fg="red")
        raise click.Abort() from error

    organisation.commit()
    db.session.commit()
    organisation.reindex()
    click.secho(f"Theme of {code} updated.", fg="green")


@theme.command("remove")
@click.argument("code")
@with_appcontext
def remove_theme(code):
    """Remove the theme of an organisation to use its compiled theme again."""
    organisation = get_organisation(code)
    if "theme" not in organisation:
        click.secho(f"Organisation {code} has no theme.", fg="yellow")
        return

    del organisation["theme"]
    organisation.commit()
    db.session.commit()
    organisation.reindex()
    click.secho(f"Theme of {code} removed.", fg="green")
