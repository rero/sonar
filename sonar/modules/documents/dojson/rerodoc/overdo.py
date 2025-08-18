# Swiss Open Access Repository
# Copyright (C) 2021 RERO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Overdo specialized class for RERODOC DOJSON transformation."""

from flask import current_app

from sonar.modules.documents.dojson.overdo import Overdo as BaseOverdo
from sonar.modules.organisations.api import OrganisationRecord


class Overdo(BaseOverdo):
    """Overdo specialized class for RERODOC DOJSON transformation."""

    registererd_organisations = []

    @staticmethod
    def create_organisation(organisation_key):
        """Create organisation if not existing and return it.

        :param str organisation_key: Key (PID) of the organisation.
        """
        if not organisation_key:
            raise Exception("No key provided")

        # Get organisation record from database
        organisation = OrganisationRecord.get_record_by_pid(organisation_key)

        if not organisation:
            # Create organisation record
            organisation = OrganisationRecord.create(
                {
                    "code": organisation_key,
                    "name": organisation_key,
                    "isShared": False,
                    "isDedicated": False,
                },
                dbcommit=True,
            )
            organisation.reindex()

    def do(self, blob, ignore_missing=True, exception_handlers=None):
        """Do transformation."""
        result = super(Overdo, self).do(blob, ignore_missing=ignore_missing, exception_handlers=exception_handlers)

        # Verify data integrity
        self.verify(result)

        # Add default license if not set.
        if not result.get("usageAndAccessPolicy"):
            default_license = "License undefined"
            if (
                result.get("organisation")
                and result["organisation"][0]["$ref"] == "https://sonar.ch/api/organisations/hepbejune"
            ):
                default_license = "CC BY-NC-SA"

            result["usageAndAccessPolicy"] = {"license": default_license}

        return result

    def get_contributor_role(self, role_700=None):
        """Return contributor role.

        :param role_700: String, role found in field 700$e
        :returns: String containing the mapped role or None
        """
        if role_700 in ["Dir.", "Codir."]:
            return "dgs"

        if role_700 == "Libr./Impr.":
            return "prt"

        if role_700 == "joint author":
            return "cre"

        if not role_700:
            doc_type = self.blob_record.get("980__", {}).get("a")

            if not doc_type:
                return None

            if doc_type in ["PREPRINT", "POSTPRINT", "DISSERTATION", "REPORT"]:
                return "cre"

            if doc_type in [
                "BOOK",
                "THESIS",
                "MAP",
                "JOURNAL",
                "PARTITION",
                "AUDIO",
                "IMAGE",
            ]:
                return "ctb"

        return None

    def verify(self, result):
        """Verify record data integrity after processing.

        :param result: Record data
        """

        def is_pa_mandatory():
            """Check if record types make provision activity mandatory."""
            document_type = result.get("documentType")

            if not document_type:
                return True

            if document_type not in [
                "coar:c_beb9",
                "coar:c_6501",
                "coar:c_998f",
                "coar:c_dcae04bc",
                "coar:c_3e5a",
                "coar:c_5794",
                "coar:c_6670",
            ]:
                return True

            return False

        self.result_ok = True

        # Check if provision activity is set, but it's optional depending
        # on record types
        if "provisionActivity" not in result and is_pa_mandatory():
            self.result_ok = False
            current_app.logger.warning(f"No provision activity found in record {result}")
