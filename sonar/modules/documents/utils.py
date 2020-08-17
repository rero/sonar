# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2019 RERO
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

"""Blueprint used for loading templates."""

from __future__ import absolute_import, print_function

from sonar.modules.utils import format_date, remove_trailing_punctuation


def publication_statement_text(provision_activity):
    """Create publication statement from place, agent and date values."""
    # Only if provision activity is imported from field 269 (no statement,
    # but start date)
    if 'statement' not in provision_activity:
        return format_date(provision_activity['startDate'])

    punctuation = {'bf:Place': ' ; ', 'bf:Agent': ', '}

    statement_with_language = {'default': ''}
    statement_type = None

    for statement in provision_activity['statement']:
        labels = statement['label']

        for label in labels:
            language = label.get('language', 'default')

            if not statement_with_language.get(language):
                statement_with_language[language] = ''

            if statement_with_language[language]:
                if statement_type == statement['type']:
                    statement_with_language[language] += punctuation[
                        statement_type]
                else:
                    if statement['type'] == 'bf:Place':
                        statement_with_language[language] += ' ; '
                    elif statement['type'] == 'Date':
                        statement_with_language[language] += ', '
                    else:
                        statement_with_language[language] += ' : '

            statement_with_language[language] += label['value']
        statement_type = statement['type']

    # date field: remove ';' and append
    for key, value in statement_with_language.items():
        value = remove_trailing_punctuation(value)
        statement_with_language[key] = value
    return statement_with_language
