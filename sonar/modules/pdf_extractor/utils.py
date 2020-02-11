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

"""Utils for PDF extraction."""

import re
import subprocess
import tempfile

import pycountry


def extract_text_from_content(content):
    """Extract full-text from content which will be stored in a temporary file.

    content is the binary representation of text.
    """
    temp = tempfile.NamedTemporaryFile(mode='w+b', suffix=".pdf")
    temp.write(content)

    return extract_text_from_file(temp.name)


def extract_text_from_file(file):
    """Extract full-text from file."""
    # Process pdf text extraction
    text = subprocess.check_output(
        'pdftotext -enc UTF-8 {file} - 2> /dev/null'.format(file=file),
        shell=True)
    text = text.decode()

    # Remove carriage returns
    text = re.sub('[\r\n\f]+', ' ', text)

    return text


def format_extracted_data(data):
    """Format the metadata extracted by Grobid service."""
    formatted_data = {}

    # Get title
    title = data['teiHeader']['fileDesc']['titleStmt']['title'].get('#text')
    if title:
        formatted_data['title'] = title

    if data['text']['@xml:lang']:
        language = pycountry.languages.get(alpha_2=data['text']['@xml:lang'])
        if language:
            if hasattr(language, 'bibliographic'):
                formatted_data['languages'] = [language.bibliographic]
            else:
                formatted_data['languages'] = [language.alpha_3]

    analytic = data['teiHeader']['fileDesc']['sourceDesc']['biblStruct'].get(
        'analytic', {})

    if analytic and analytic.get('author'):
        authors = force_list(analytic.get('author'))

        for author in authors:
            author_data = {}

            if author.get('persName'):
                name = []
                surname = author['persName'].get('surname')

                if surname:
                    name.append(surname)

                forenames = author['persName'].get('forename', [])
                forenames = force_list(forenames)

                name = name + [forename['#text'] for forename in forenames]

                author_data['name'] = ' '.join(name)

            if author_data.get('name'):
                affiliations = force_list(author.get('affiliation', []))

                if affiliations:
                    affiliation = affiliations[0]
                    organisations = force_list(affiliation.get('orgName', []))

                    for organisation in organisations:
                        if organisation.get('@type') == 'institution':
                            author_data['affiliation'] = organisation['#text']

            formatted_data.setdefault('authors', []).append(author_data)

    imprint = data['teiHeader']['fileDesc']['sourceDesc']['biblStruct'][
        'monogr'].get('imprint', {})

    if imprint:
        if imprint.get('publisher'):
            formatted_data['journal'] = {'name': imprint['publisher']}

            imprint['biblScope'] = force_list(imprint['biblScope'])

            for item in imprint['biblScope']:
                if item['@unit'] in ['page', 'volume', 'number']:
                    key = item['@unit']
                    if key == 'page':
                        key = 'pages'

                    formatted_data['journal'][
                        key] = item['#text'] if '#text' in item else item[
                            '@from'] + '-' + item['@to']

    abstract = data['teiHeader']['profileDesc'].get('abstract')
    if abstract:
        formatted_data['abstract'] = abstract['p']

    return formatted_data


def force_list(data):
    """Force input data to be a list."""
    if not isinstance(data, list):
        return [data]

    return data
