# Swiss Open Access Repository
# Copyright (C) 2022 RERO
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

"""Test sitemap views."""

import mock
from flask import Response, url_for


def response_urlset():
    """."""
    return Response(
        """
    <?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>http://www.domain.com/document/1</loc>
            <lastmod>2022-01-01</lastmod>
        </url>
    </urlset>
    """
    )


def response_sitemapindex():
    """."""
    return Response(
        """
    <?xml version="1.0" encoding="UTF-8"?>
    <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <sitemap>
            <loc>http://www.domain.com/sitemap_1.xml</loc>
        </itemap>
    </urlset>
    """
    )


def test_sitemap_file_error(app, client):
    """File Not Found abort 404 if file doen't exists."""
    url = url_for("sitemap.sitemap", view="global")
    res = client.get(url)
    assert res.status_code == 404


@mock.patch(
    "sonar.modules.sitemap.views.response_file",
    mock.MagicMock(return_value=response_urlset()),
)
def test_sitemap_file(app, client):
    """Test entrypoint for sitemap urlset."""
    url = url_for("sitemap.sitemap", view="global")
    res = client.get(url)
    assert res.status_code == 200


@mock.patch(
    "sonar.modules.sitemap.views.response_file",
    mock.MagicMock(return_value=response_sitemapindex()),
)
def test_sitemap_index_file(app, client):
    """Test entrypoint for sitemap index."""
    url = url_for("sitemap.sitemap_index", view="global", index=1)
    res = client.get(url)
    assert res.status_code == 200
