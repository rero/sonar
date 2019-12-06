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
        'pdftotext -enc UTF-8 {file} -'.format(file=file), shell=True)
    text = text.decode()

    # Remove carriage returns
    text = re.sub('[\r\n\f]+', ' ', text)

    return text


def format_extracted_data(data):
    """Format the extracted metadata from PDF."""
    formatted_data = {}
    if '#text' in data['teiHeader']['fileDesc']['titleStmt']['title']:
        formatted_data['title'] = data['teiHeader']['fileDesc']['titleStmt'][
            'title']['#text']

    if data['text']['@xml:lang']:
        language = pycountry.languages.get(alpha_2=data['text']['@xml:lang'])
        if language:
            if hasattr(language, 'bibliographic'):
                formatted_data['languages'] = [language.bibliographic]
            else:
                formatted_data['languages'] = [language.alpha_3]

    if 'analytic' in data['teiHeader']['fileDesc']['sourceDesc'][
            'biblStruct'] and data['teiHeader']['fileDesc']['sourceDesc'][
                'biblStruct']['analytic'] and 'author' in data['teiHeader'][
                    'fileDesc']['sourceDesc']['biblStruct']['analytic']:
        authors = data['teiHeader']['fileDesc']['sourceDesc']['biblStruct'][
            'analytic']['author']
        if not isinstance(authors, list):
            authors = [authors]

        formatted_data['authors'] = []
        for author in authors:
            if 'persName' in author:
                new_author = {}

                if 'surname' in author['persName']:
                    new_author['name'] = author['persName']['surname']

                if not isinstance(author['persName']['forename'], list):
                    author['persName']['forename'] = [
                        author['persName']['forename']
                    ]

                for forename in author['persName']['forename']:
                    new_author[
                        'name'] = forename['#text'] + ' ' + new_author['name']

                formatted_data['authors'].append(new_author)

    if data['teiHeader']['fileDesc']['sourceDesc']['biblStruct']['monogr'][
            'imprint']:
        imprint = data['teiHeader']['fileDesc']['sourceDesc']['biblStruct'][
            'monogr']['imprint']
        if 'publisher' in imprint:
            formatted_data['journal'] = {'name': imprint['publisher']}

            if not isinstance(imprint['biblScope'], list):
                imprint['biblScope'] = [imprint['biblScope']]

            for item in imprint['biblScope']:
                if item['@unit'] in ['page', 'volume', 'number']:
                    key = item['@unit']
                    if key == 'page':
                        key = 'pages'

                    formatted_data['journal'][
                        key] = item['#text'] if '#text' in item else item[
                            '@from'] + '-' + item['@to']

    if 'abstract' in data['teiHeader']['profileDesc'] and data['teiHeader'][
            'profileDesc']['abstract']:
        formatted_data['abstract'] = data['teiHeader']['profileDesc'][
            'abstract']['p']

    return formatted_data
