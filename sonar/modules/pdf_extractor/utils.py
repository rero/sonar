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
