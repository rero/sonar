# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Mapping from COAR resource type to CSL-JSON item type."""

#: Maps a SONAR/COAR documentType value to a CSL-JSON type.
#: See https://docs.citationstyles.org/en/stable/specification.html#appendix-iii-types
#: Mirrors the COAR classification already established in
#: sonar/modules/documents/serializers/schemas/schemaorg.py, translated to
#: the closest CSL-JSON type. Falls back to "document" when no clean CSL
#: equivalent exists, rather than guessing a close-but-wrong type.
TYPE_MAPPING = {
    "coar:c_2f33": "book",
    "coar:c_3248": "chapter",
    "coar:c_c94f": "document",
    "coar:c_5794": "paper-conference",
    "coar:c_18cp": "paper-conference",
    "coar:c_6670": "graphic",
    "coar:c_18co": "graphic",
    "coar:c_f744": "book",
    "coar:c_ddb1": "dataset",
    "coar:c_3e5a": "article-journal",
    "coar:c_beb9": "article-journal",
    "coar:c_6501": "article-journal",
    "coar:c_998f": "article-newspaper",
    "coar:c_dcae04bc": "article-journal",
    "coar:c_8544": "speech",
    "non_textual_object": "document",
    "coar:c_8a7e": "motion_picture",
    "coar:c_ecc8": "graphic",
    "coar:c_12cc": "map",
    "coar:c_18cc": "broadcast",
    "coar:c_18cw": "musical_score",
    "coar:c_5ce6": "software",
    "coar:c_15cd": "patent",
    "coar:c_2659": "periodical",
    "coar:c_0640": "periodical",
    "coar:c_2cd9": "periodical",
    "coar:c_2fe3": "periodical",
    "coar:c_816b": "article-journal",
    "coar:c_93fc": "report",
    "coar:c_18ww": "report",
    "coar:c_18wz": "report",
    "coar:c_18wq": "report",
    "coar:c_186u": "report",
    "coar:c_18op": "report",
    "coar:c_ba1f": "report",
    "coar:c_18hj": "report",
    "coar:c_18ws": "report",
    "coar:c_18gh": "report",
    "coar:c_46ec": "thesis",
    "coar:c_7a1f": "thesis",
    "coar:c_db06": "thesis",
    "coar:c_bdcc": "thesis",
    "habilitation_thesis": "thesis",
    "advanced_studies_thesis": "thesis",
    "other_thesis": "thesis",
    "coar:c_8042": "document",
    "coar:c_1843": "document",
    "coar:R60J-J5BD": "document",
    "coar:c_ba08": "review-book",
}
