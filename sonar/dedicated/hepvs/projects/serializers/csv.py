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

"""CSV serializer for HEP Valais projects."""

from sonar.resources.projects.serializers.csv import CSVSerializer as BaseCSVSerializer


class CSVSerializer(BaseCSVSerializer):
    """CSV serializer for HEP Valais projects."""

    chunk_size = 1000
    list_separator = "|"

    def format_row(self, data):
        """Format the data for a single row.

        :param data: Data dictionary.
        """

        def transform_external_partners(external_partner):
            """Convert external partner object into string.

            :param external_partner: External partner dictionary.
            :returns: String representation of the partner.
            """
            text = external_partner["searcherName"]
            if external_partner.get("institution"):
                text = f"{text} ({external_partner['institution']})"
            return text

        def transform_actors_involved(actor):
            """Convert actor object into string.

            :param actor: Actor dictionary.
            :returns: String representation of the actor.
            """
            text = actor["choice"] if actor["choice"] != "Other" else actor["other"]
            if actor.get("count"):
                text = f"{text} ({actor['count']})"
            return text

        for key in ["innerSearcher", "keywords", "realizationFramework"]:
            if data.get(key):
                data[key] = self.list_separator.join(data[key])

        # External partners
        if data.get("externalPartners"):
            if not data["externalPartners"]["choice"]:
                data.pop("externalPartners")
            else:
                data["externalPartners"] = self.list_separator.join(
                    list(
                        map(
                            transform_external_partners,
                            data["externalPartners"]["list"],
                        )
                    )
                )

        # Actors involved
        if data.get("actorsInvolved"):
            data["actorsInvolved"] = self.list_separator.join(
                list(map(transform_actors_involved, data["actorsInvolved"]))
            )

        # Educational document
        if data.get("educationalDocument"):
            if not data["educationalDocument"]["choice"]:
                data.pop("educationalDocument")
            else:
                data["educationalDocument"] = data["educationalDocument"]["briefDescription"]

        # Funder
        if not data.get("funding", {}).get("choice"):
            data.pop("funding", None)

        # Related to mandate
        if not data.get("relatedToMandate", {}).get("choice"):
            data.pop("relatedToMandate", None)

        # Promote innovation
        if data.get("promoteInnovation"):
            if not data["promoteInnovation"]["choice"]:
                data.pop("promoteInnovation")
            else:
                data["promoteInnovation"] = data["promoteInnovation"]["reason"]
