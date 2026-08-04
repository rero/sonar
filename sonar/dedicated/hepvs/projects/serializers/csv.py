# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""CSV serializer for HEP Valais projects."""

from sonar.resources.projects.serializers.csv import CSVSerializerMixin


class CSVSerializer(CSVSerializerMixin):
    """CSV serializer for HEP Valais projects."""

    chunk_size = 1000

    def __init__(self):
        """Constructor."""
        self.list_separator = "|"
        super().__init__(
            csv_included_fields=[
                "pid",
                "name",
                "approvalDate",
                "projectSponsor",
                "statusHep",
                "mainTeam",
                "innerSearcher",
                "secondaryTeam",
                "externalPartners",
                "status",
                "startDate",
                "endDate",
                "description",
                "keywords",
                "realizationFramework",
                "funding_funder_type",
                "funding_funder_name",
                "funding_funder_number",
                "funding_fundingReceived",
                "actorsInvolved",
                "benefits",
                "impactOnFormation",
                "impactOnProfessionalEnvironment",
                "impactOnPublicAction",
                "promoteInnovation",
                "relatedToMandate_mandate",
                "relatedToMandate_name",
                "relatedToMandate_briefDescription",
                "educationalDocument",
                "searchResultsValorised",
            ],
            csv_excluded_fields=[],
            header_separator="_",
        )

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
            text = actor["choice"]
            if text == "Other":
                text = actor.get("other", text)
            if actor.get("count"):
                text = f"{text} ({actor['count']})"
            return text

        for key in ["innerSearcher", "keywords", "realizationFramework"]:
            if data.get(key):
                data[key] = self.list_separator.join(data[key])

        # External partners
        if data.get("externalPartners"):
            if not data["externalPartners"].get("choice"):
                data.pop("externalPartners")
            else:
                data["externalPartners"] = self.list_separator.join(
                    list(
                        map(
                            transform_external_partners,
                            data["externalPartners"].get("list", []),
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
            if not data["educationalDocument"].get("choice"):
                data.pop("educationalDocument")
            else:
                data["educationalDocument"] = data["educationalDocument"].get("briefDescription", "")

        # Funder
        if not data.get("funding", {}).get("choice"):
            data.pop("funding", None)

        # Related to mandate
        if not data.get("relatedToMandate", {}).get("choice"):
            data.pop("relatedToMandate", None)

        # Promote innovation
        if data.get("promoteInnovation"):
            if not data["promoteInnovation"].get("choice"):
                data.pop("promoteInnovation")
            else:
                data["promoteInnovation"] = data["promoteInnovation"].get("reason", "")
