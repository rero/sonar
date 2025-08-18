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

"""Test sitemap."""

import os
import shutil
import xml.etree.ElementTree as ET
from datetime import date

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.sitemap.sitemap import sitemap_generate


def test_sitemap(app, db, organisation, document):
    """Test sitemap generator."""
    # Set current directory on static_folder config
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "sitemap")
    app.config["SONAR_APP_SITEMAP_FOLDER_PATH"] = path
    # namespace of sitemap
    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"

    sitemap_generate("org.domain.com", 10)

    sitemap_file = os.path.join(path, "sitemap.xml")
    assert os.path.isfile(sitemap_file)

    # Control data into the xml file
    tree = ET.parse(sitemap_file)
    url = tree.findall(f"{namespace}url")[0]
    assert url.find(f"{namespace}loc").text == "https://sonar.rero.ch/global/documents/1"
    assert date.today().strftime("%Y-%m-%d") == url.find(f"{namespace}lastmod").text

    # ------- test for a dedicated organisation
    organisation["isDedicated"] = True
    organisation["serverName"] = "org.domain.com"
    organisation.commit()
    organisation.reindex()
    db.session.commit()

    sitemap_generate("org.domain.com", 10)

    sitemap_file = os.path.join(path, organisation["pid"], "sitemap.xml")
    assert os.path.isfile(sitemap_file)

    # Control data into the xml file
    tree = ET.parse(sitemap_file)
    url = tree.findall(f"{namespace}url")[0]
    assert url.find(f"{namespace}loc").text == "https://org.domain.com/org/documents/1"
    assert date.today().strftime("%Y-%m-%d") == url.find(f"{namespace}lastmod").text

    # ------- Generate multiple files with index sitemap
    document.pop("pid", None)
    document.pop("_oai", None)
    document["identifiedBy"] = [{"value": "R003415714", "type": "bf:Local", "source": "RERO"}]
    doc = DocumentRecord.create(document)
    doc.reindex()
    db.session.commit()

    sitemap_generate("org.domain.com", 1)

    sitemap_index = os.path.join(path, organisation["pid"], "sitemap.xml")
    assert os.path.isfile(sitemap_index)

    tree = ET.parse(sitemap_index)
    sitemaps = tree.findall(f"{namespace}sitemap")
    for n, sitemap in enumerate(sitemaps, start=1):
        assert f"https://org.domain.com/org/sitemap_{n}.xml" == sitemap.find(f"{namespace}loc").text

    for i in range(1, 3):
        sitemap_file = os.path.join(path, organisation["pid"], f"sitemap_{i}.xml")
        assert os.path.isfile(sitemap_file)
        tree = ET.parse(sitemap_file)
        url = tree.findall(f"{namespace}url")[0]
        assert f"https://org.domain.com/org/documents/{i}" == url.find(f"{namespace}loc").text
        assert date.today().strftime("%Y-%m-%d") == url.find(f"{namespace}lastmod").text

    # Remove folder after test
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
