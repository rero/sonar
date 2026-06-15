# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Stats record API."""

from functools import partial

from invenio_db import db

from sonar.modules.documents.api import DocumentSearch
from sonar.modules.organisations.api import OrganisationSearch

from ..api import SonarIndexer, SonarRecord, SonarSearch
from ..fetchers import id_fetcher
from ..providers import Provider
from .config import Configuration
from .minters import id_minter

# provider
RecordProvider = type("RecordProvider", (Provider,), {"pid_type": Configuration.pid_type})
# minter
pid_minter = partial(id_minter, provider=RecordProvider)
# fetcher
pid_fetcher = partial(id_fetcher, provider=RecordProvider)


class Record(SonarRecord):
    """Stats record."""

    minter = pid_minter
    fetcher = pid_fetcher
    provider = RecordProvider
    schema = Configuration.schema

    @classmethod
    def collect(cls, save=True):
        """Collect statistics.

        :params bool save: Wether the stats collected are saved into DB
        :returns: Stats record object
        :rtype: Record
        """

        def has_fulltext_file(document):
            """Check if document has at least a full-text file.

            :param dict document: Document dictionary
            :returns: True if document has a full-text file
            :rtype: bool
            """
            for file in document.get("_files", []):
                if file.get("mimetype") == "application/pdf" and file.get("type") == "file":
                    return True

            return False

        stats = []
        for organisation in OrganisationSearch().get_shared_or_dedicated_list():
            documents = cls.get_documents(organisation["pid"])
            fulltext = 0
            pids = []

            for document in documents:
                document = document.to_dict()

                # Add PID to list.
                pids.append(document["pid"])

                # Increment fulltext counter.
                if has_fulltext_file(document):
                    fulltext = fulltext + 1

            stats.append(
                {
                    "organisation": organisation["name"],
                    "type": ("dedicated" if organisation.to_dict().get("isDedicated") else "shared"),
                    "full_text": fulltext,
                    "pids": pids,
                }
            )

        record = cls.create({"values": stats})

        if save:
            record.commit()
            db.session.commit()
            record.reindex()

        return record

    @classmethod
    def get_documents(cls, organisation_pid):
        """Get documents for organisation.

        :param str organisation_pid: Organisation PID.
        :returns: A generator for getting documents PID and files.
        :rtype: generator
        """
        query = DocumentSearch().filter("term", organisation__pid=organisation_pid).source(["pid", "_files"])

        return query.scan()


class RecordSearch(SonarSearch):
    """Record search."""

    class Meta:
        """Search only on item index."""

        index = Configuration.index
        doc_types = []


class RecordIndexer(SonarIndexer):
    """Indexing documents in Elasticsearch."""

    record_cls = Record
