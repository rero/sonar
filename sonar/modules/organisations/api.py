# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Organisation Api."""

from functools import partial

from flask import has_request_context
from flask.globals import request_ctx
from werkzeug.local import LocalProxy

from sonar.modules.users.api import current_user_record

from ..api import SonarIndexer, SonarRecord, SonarSearch
from ..fetchers import id_fetcher
from ..providers import Provider
from .minters import id_minter


def get_current_organisation():
    """Return current organisation from context."""
    if not has_request_context():
        return None
    if not hasattr(request_ctx, "organisation_record"):
        request_ctx.organisation_record = (
            None
            if (not current_user_record or not current_user_record.get("organisation"))
            else OrganisationRecord.get_record_by_ref_link(current_user_record["organisation"]["$ref"])
        )

    return getattr(request_ctx, "organisation_record", None)


current_organisation = LocalProxy(get_current_organisation)

# provider
OrganisationProvider = type("OrganisationProvider", (Provider,), {"pid_type": "org"})
# minter
organisation_pid_minter = partial(id_minter, provider=OrganisationProvider)
# fetcher
organisation_pid_fetcher = partial(id_fetcher, provider=OrganisationProvider)


class OrganisationSearch(SonarSearch):
    """Search organisations."""

    class Meta:
        """Search only on item index."""

        index = "organisations"
        doc_types = []

    def get_shared_or_dedicated_list(self):
        """Get the list of dedicated or shared organisations.

        :returns: Iterator of dedicated or shared organisations.
        """
        return (
            self.filter(
                "bool",
                should=[{"term": {"isDedicated": True}}, {"term": {"isShared": True}}],
            )
            .source(["pid", "name", "isShared", "isDedicated"])
            .execute()
            .hits
        )

    def get_organisation_pid_by_server_name(self, server_name):
        """Get organisation by server_name.

        :param server_name: server name for the dedicated organisation.
        :returns: pid of the dedicated organisation.
        """
        if hits := self.filter("term", serverName=server_name).source(["pid"]).execute().hits:
            return hits[0].pid
        return None

    def get_dedicated_list(self):
        """Get the list of dedicated organisations.

        :returns: Iterator of dedicated organisations.
        """
        return self.filter("term", isDedicated=True).execute().hits

    def get_organisation_from_naan(self, naan):
        """Get organisation from a given naan.

        :param naan: Name Assigning Authority Number for the dedicated
                     organisation.
        :returns: pid of the dedicated organisation.
        """
        try:
            return next(self.filter("term", arkNAAN=naan).scan())
        except StopIteration:
            return None


class OrganisationRecord(SonarRecord):
    """Organisation record class."""

    minter = organisation_pid_minter
    fetcher = organisation_pid_fetcher
    provider = OrganisationProvider
    schema = "organisations/organisation-v1.0.0.json"

    @classmethod
    def create(cls, data, id_=None, dbcommit=False, with_bucket=True, **kwargs):
        """Create an organisation record.

        :param data: The metadata of the record.
        :param id_: The id of the record.
        :param dbcommit: If True commit the changes to the database.
        :param with_bucket: If True create a bucket for the organisation.
        :returns: The created record.
        """

        return super().create(data, id_=id_, dbcommit=dbcommit, with_bucket=with_bucket, **kwargs)

    @classmethod
    def get_or_create(cls, code, name=None):
        """Get or create an organisation.

        :param code: Organisation's code, equivalent to PID.
        :param name: Organisation's name.
        :returns: Organisations object.
        """
        organisation = cls.get_record_by_pid(code)

        if organisation:
            return organisation

        organisation = cls.create({"code": code, "name": name if name else code}, dbcommit=True)
        organisation.reindex()
        return organisation


class OrganisationIndexer(SonarIndexer):
    """Indexing documents in Elasticsearch."""

    record_cls = OrganisationRecord
