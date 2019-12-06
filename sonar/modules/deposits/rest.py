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

"""Deposit rest views."""

from __future__ import absolute_import, print_function

import re
from io import BytesIO

from flask import Blueprint, abort, jsonify, make_response, request
from invenio_db import db
from invenio_rest import ContentNegotiatedMethodView

from sonar.modules.deposits.api import DepositRecord
from sonar.modules.pdf_extractor.pdf_extractor import PDFExtractor
from sonar.modules.pdf_extractor.utils import format_extracted_data


class FilesResource(ContentNegotiatedMethodView):
    """Rest file management."""

    @staticmethod
    def get(pid=None):
        """Get list of files associated with bucket."""
        deposit = DepositRecord.get_record_by_pid(pid)
        return make_response(jsonify(deposit.files.dumps()))

    @staticmethod
    def post(pid=None):
        """Save the file and associate it to the deposit record."""
        deposit = DepositRecord.get_record_by_pid(pid)

        if not deposit:
            abort(400)

        if 'key' not in request.args or 'type' not in request.args:
            abort(400)

        # Type must be either "main" or "additional"
        if request.args['type'] not in ['main', 'additional']:
            abort(400)

        key = request.args['key']

        # Store full-text in a file
        # text_key = change_filename_extension(key, 'txt')
        # deposit.files[text_key] = BytesIO(
        #     extract_text_from_content(request.get_data()).encode())
        # deposit.files[text_key]['category'] = request.args['type']
        # deposit.files[text_key]['file_type'] = 'full-text'
        # deposit.commit()

        file_content = BytesIO(request.get_data())

        # Store document
        deposit.files[key] = file_content
        deposit.files[key]['label'] = re.search(r'(.*)\..*$', key).group(1)
        deposit.files[key]['embargo'] = False
        deposit.files[key]['embargoDate'] = None
        deposit.files[key]['expect'] = False
        deposit.files[key]['category'] = request.args['type']
        deposit.files[key]['file_type'] = 'file'

        # Extract data from pdf and populate deposit
        if request.args['type'] == 'main':
            pdf_extractor = PDFExtractor()
            pdf_metadata = format_extracted_data(
                pdf_extractor.process_raw(request.get_data()))

            # deposit.populate_with_pdf_metadata(
            #     pdf_metadata, "Deposit #{pid}".format(pid=pid))
            deposit.files[key]['pdf_metadata'] = pdf_metadata

        deposit.commit()
        db.session.commit()

        return make_response(jsonify(deposit.files[key].dumps()))


class FileResource(ContentNegotiatedMethodView):
    """Deposit file resource."""

    @staticmethod
    def put(pid=None, key=None):
        """Update metadata linked to file."""
        deposit = DepositRecord.get_record_by_pid(pid)

        if not deposit:
            abort(400)

        json = request.get_json()

        if key not in deposit.files:
            abort(400)

        for item in json.items():
            deposit.files[key][item[0]] = item[1]

        deposit.commit()
        db.session.commit()

        return make_response(jsonify(deposit.files[key].dumps()))


files_view = FilesResource.as_view('files')
file_view = FileResource.as_view('file')

blueprint = Blueprint('deposits', __name__, url_prefix='/deposits/<pid>/')
blueprint.add_url_rule('/custom-files/<key>', view_func=file_view)
blueprint.add_url_rule('/custom-files', view_func=files_view)
