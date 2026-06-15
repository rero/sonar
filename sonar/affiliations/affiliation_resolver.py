# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Affiliations resolver."""

import csv

from fuzzywuzzy import fuzz
from werkzeug.utils import cached_property

CSV_FILE = "./data/affiliations.csv"


class AffiliationResolver:
    """Affiliation resolver."""

    @cached_property
    def affiliations(self):
        """List of affiliations retrieved from a dedicated file.

        :returns: List of affliations
        """
        affiliations = []

        with open(CSV_FILE) as file:
            reader = csv.reader(file, delimiter="\t")
            for row in reader:
                affiliation = []
                for index, value in enumerate(row):
                    if index > 0 and value:
                        affiliation.append(value)

                if affiliation:
                    affiliations.append(affiliation)

        return affiliations

    def resolve(self, searched_affiliation):
        """Resolve affiliations from given parameter.

        :param searched_affiliation: Affiliation to match.
        :returns: String of matching affiliation.
        """
        if not searched_affiliation:
            return None

        collected_affiliations = []
        for affiliations in self.affiliations:
            # the first string in the row is the standard form, to be stored
            standard_form = affiliations[0]
            for affiliation in affiliations:
                score = fuzz.partial_ratio(searched_affiliation, affiliation)
                if score > 92 and standard_form not in collected_affiliations:
                    # handle special case UZH / ZHdK
                    # TODO: solve this special case by converting the CSV file to JSON
                    # using rejected forms https://github.com/rero/sonar/issues/824
                    if (
                        affiliation.lower() == "zurich university"
                        and "zurich university of the arts" in searched_affiliation.lower()
                    ):
                        continue
                    # handle special case CERN/Lucerne
                    if affiliation.lower() == "cern" and "lucerne" in searched_affiliation.lower():
                        continue
                    # handle special case Freiburg im Breisgau
                    if "university of freiburg" in searched_affiliation.lower():
                        break

                    collected_affiliations.append(standard_form)
        return collected_affiliations
