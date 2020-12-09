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

"""Test Archive ouverte UNIGE record loader."""

from sonar.modules.documents.loaders.schemas.archive_ouverte_unige import \
    ArchiveOuverteUnigeSchema


def test_archive_ouverte_unige_loader():
    """Test Archive ouverte UNIGE record loader."""
    xml = """
<record>
    <header>
        <identifier>oai:unige.ch:unige:1</identifier>
        <datestamp>2016-07-18T10:53:09Z</datestamp>
        <setSpec>archive-ouverte</setSpec>
    </header>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:leader>00000naa a2200000 c 4500</marc:leader>
                <marc:controlfield tag="001">unige:1</marc:controlfield>
                <marc:datafield ind1=" " ind2=" " tag="022">
                    <marc:subfield code="a">0378-5173</marc:subfield>
                </marc:datafield>
                <marc:datafield ind1="7" ind2=" " tag="024">
                    <marc:subfield code="2">DOI</marc:subfield>
                    <marc:subfield code="a">10.1016/j.ijpharm</marc:subfield>
                </marc:datafield>
                <marc:datafield ind1="7" ind2=" " tag="024">
                    <marc:subfield code="2">PMID</marc:subfield>
                    <marc:subfield code="a">17997238</marc:subfield>
                </marc:datafield>
                <marc:datafield ind1="7" ind2=" " tag="024">
                    <marc:subfield code="2">OTHERID</marc:subfield>
                    <marc:subfield code="a">123456789</marc:subfield>
                </marc:datafield>
                <marc:datafield ind1=" " ind2=" " tag="035">
                    <marc:subfield code="a">R004655041</marc:subfield>
                </marc:datafield>
                <marc:datafield ind1=" " ind2=" " tag="041">
                    <marc:subfield code="a">eng</marc:subfield>
                </marc:datafield>
                <marc:datafield ind1=" " ind2=" " tag="082">
                    <marc:subfield code="a">615</marc:subfield>
                </marc:datafield>
                <marc:datafield ind1="1" ind2="0" tag="245">
                    <marc:subfield code="a">High throughput</marc:subfield>
                </marc:datafield>
                <marc:datafield ind1=" " ind2=" " tag="506">
                    <marc:subfield code="f">Restricted access</marc:subfield>
                </marc:datafield>
                <marc:datafield ind1=" " ind2=" " tag="520">
                    <marc:subfield code="a">
                        Spectroscopic methods.
                    </marc:subfield>
                </marc:datafield>
                <marc:datafield ind1=" " ind2=" " tag="653">
                    <marc:subfield code="a">
                        Drug Delivery Systems
                    </marc:subfield>
                </marc:datafield>
                <marc:datafield ind1=" " ind2=" " tag="653">
                    <marc:subfield code="a">Hirudins</marc:subfield>
                </marc:datafield>
                <marc:datafield ind1=" " ind2=" " tag="653">
                    <marc:subfield code="a">Permeability</marc:subfield>
                </marc:datafield>
                <marc:datafield ind1=" " ind2=" " tag="653">
                    <marc:subfield code="a">Proteins</marc:subfield>
                </marc:datafield>
                <marc:datafield ind1=" " ind2=" " tag="653">
                    <marc:subfield code="a">Serum Albumin</marc:subfield>
                </marc:datafield>
                <marc:datafield ind1=" " ind2=" " tag="653">
                    <marc:subfield code="a">Bovine</marc:subfield>
                </marc:datafield>
                <marc:datafield ind1=" " ind2=" " tag="653">
                    <marc:subfield code="a">Spectrometry</marc:subfield>
                </marc:datafield>
                <marc:datafield ind1=" " ind2=" " tag="700">
                    <marc:subfield code="a">
                        Capelle, Martinus A. H.
                    </marc:subfield>
                    <marc:subfield code="8">1</marc:subfield>
                </marc:datafield>
                <marc:datafield ind1=" " ind2=" " tag="700">
                    <marc:subfield code="a">Gurny, Robert</marc:subfield>
                    <marc:subfield code="8">2</marc:subfield>
                    <marc:subfield code="9">24779</marc:subfield>
                </marc:datafield>
                <marc:datafield ind1=" " ind2=" " tag="700">
                    <marc:subfield code="a">Arvinte, Tudor</marc:subfield>
                    <marc:subfield code="8">3</marc:subfield>
                    <marc:subfield code="9">134040</marc:subfield>
                </marc:datafield>
                <marc:datafield ind1=" " ind2=" " tag="773">
                    <marc:subfield code="t">
                        International Journal of Pharmaceutics
                    </marc:subfield>
                    <marc:subfield code="v">350</marc:subfield>
                    <marc:subfield code="p">272-278</marc:subfield>
                    <marc:subfield code="y">2008</marc:subfield>
                </marc:datafield>
                <marc:datafield ind1="4" ind2=" " tag="856">
                    <marc:subfield code="3">Record</marc:subfield>
                    <marc:subfield code="u">
                        http://archive-ouverte.unige.ch/unige:1
                    </marc:subfield>
                </marc:datafield>
                <marc:datafield ind1="4" ind2=" " tag="856">
                    <marc:subfield code="3">Article</marc:subfield>
                    <marc:subfield code="f">ATTACHMENT01</marc:subfield>
                    <marc:subfield code="u">
                        http://archive-ouverte.unige.ch/unige:1/ATTACHMENT01
                    </marc:subfield>
                    <marc:subfield code="x">Restricted access</marc:subfield>
                    <marc:subfield code="y">
                        Article (Published version)
                    </marc:subfield>
                </marc:datafield>
                <marc:datafield ind1=" " ind2=" " tag="920">
                    <marc:subfield code="a">
                        Université de Genève
                    </marc:subfield>
                </marc:datafield>
                <marc:datafield ind1=" " ind2=" " tag="928">
                    <marc:subfield code="a">
                        Faculté des sciences; Section des sciences
                    </marc:subfield>
                    <marc:subfield code="c">17</marc:subfield>
                </marc:datafield>
                <marc:datafield ind1=" " ind2=" " tag="929">
                    <marc:subfield code="a">
                        Department of Pharmaceutics and Biopharmaceutics.
                    </marc:subfield>
                </marc:datafield>
                <marc:datafield ind1=" " ind2=" " tag="930">
                    <marc:subfield code="a">1</marc:subfield>
                </marc:datafield>
                <marc:datafield ind1=" " ind2=" " tag="980">
                    <marc:subfield code="a">Article</marc:subfield>
                    <marc:subfield code="b">
                        Article scientifique
                    </marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    """
    assert ArchiveOuverteUnigeSchema().dump(xml) == {
        'identifiedBy': [{
            'source': 'Archive ouverte UNIGE',
            'type': 'bf:Local',
            'value': 'unige:1'
        }, {
            'type': 'bf:Doi',
            'value': '10.1016/j.ijpharm'
        }, {
            'source': 'PMID',
            'type': 'bf:Local',
            'value': '17997238'
        }],
        'title': [{
            'mainTitle': [{
                'language': 'eng',
                'value': 'High throughput'
            }],
            'type':
            'bf:Title'
        }]
    }
