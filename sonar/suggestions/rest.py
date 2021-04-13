# -*- coding: utf-8 -*-
#
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

"""Suggestions rest views."""

from flask import Blueprint, current_app, jsonify, request

from sonar.proxies import sonar

blueprint = Blueprint('suggestions', __name__, url_prefix='/suggestions')


@blueprint.route('/completion', methods=['GET'])
def completion():
    """Suggestions completion."""
    query = request.args.get('q')
    field = request.args.get('field')
    resource = request.args.get('resource')

    if not query:
        return jsonify({'error': 'No query parameter given'}), 400

    if not field:
        return jsonify({'error': 'No field parameter given'}), 400

    if not resource:
        return jsonify({'error': 'No resource parameter given'}), 400

    # Suggestions from multiple fields possible
    fields = field.split(',')

    search = None
    try:
        service = sonar.service(resource)
        search = service.config.search_cls(index=resource)
    except Exception:
        for doc_type, config in current_app.config.get(
                'RECORDS_REST_ENDPOINTS').items():
            if config.get('search_index') == resource:
                search = config['search_class']()

    if not search:
        return jsonify({'error': 'Search class not found'}), 404

    results = []

    try:
        search = search.source(excludes="*")

        for field in fields:
            search = search.suggest(field,
                                    query,
                                    completion={
                                        'field': field,
                                        'skip_duplicates': True
                                    })
        for i, suggestion in search.execute().suggest.to_dict().items():
            results = results + [
                option['text'] for option in suggestion[0]['options']
            ]
    except Exception:
        return jsonify({'error': 'Bad request'}), 400

    # Remove duplicates
    results = list(dict.fromkeys(results))

    # Sort items
    results.sort()

    return jsonify(results)
