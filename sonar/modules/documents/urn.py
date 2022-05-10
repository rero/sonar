# -*- coding: utf-8 -*-
#
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

"""Urn API."""


from flask import current_app
from invenio_pidstore.errors import PIDAlreadyExists
from invenio_pidstore.models import PersistentIdentifier, PIDStatus


class Urn:
    """Urn class."""

    @classmethod
    def _calculateCheckDigit(cls, urn):
        """Return the check-digit calculated on a URN.

        :param urn: the urn identifier.
        """
        # For details on the algorithm, see:
        # https://d-nb.info/1045320641/34
        # set up conversion table
        conversion_table = {
            '0':'1', '1':'2', '2':'3', '3':'4', '4':'5', '5':'6', '6':'7',
            '7':'8', '8':'9', '9':'41', 'A':'18', 'B':'14', 'C':'19', 'D':'15',
            'E':'16', 'F':'21', 'G':'22', 'H':'23', 'I':'24', 'J':'25',
            'K':'42', 'L':'26', 'M':'27', 'N':'13', 'O':'28', 'P':'29',
            'Q':'31', 'R':'12', 'S':'32', 'T':'33', 'U':'11', 'V':'34',
            'W':'35', 'X':'36', 'Y':'37', 'Z':'38', '-':'39', ':':'17',
            '_':'43', '.':'47', '/':'45','+':'49'
            }
        # obtain digit sequence using the conversion table by concatenating
        # chars
        digit_sequence = ''
        for idx, element in enumerate(urn, 0):
            digits = conversion_table[urn[idx].upper()]
            digit_sequence = digit_sequence + digits
        # calculate product sum
        product_sum = 0
        for idx, element in enumerate(digit_sequence, 0):
            product_sum = product_sum + ((idx+1) * int(digit_sequence[idx]))
        # read the last number of the digit sequence and calculate the quotient
        last_number = int(digit_sequence[-1])
        quotient = int(product_sum/last_number)
        quotient_string = str(quotient)
        # read the check-digit from the quotient value string        
        return quotient_string[-1]

    @classmethod
    def _generate_urn(cls, pid, config):
        """Generate a URN code for namespace.

        :param pid: the pid of the urn identifier.
        :param config: organisation related configuration.
        """
        new_urn = f'{config.get("namespace")}-{config.get("code"):03}-{pid}'
        return f'{new_urn}{cls._calculateCheckDigit(new_urn)}'

    @classmethod
    def create_urn(cls, record):
        """Create the URN identifier.

        :param record: the invenio record instance to be processed.
        """
        urn_config = current_app.config.get("SONAR_APP_DOCUMENT_URN")
        org_pid = record.replace_refs().get("organisation", [{}])[0].get("pid")
        if config := urn_config.get("organisations", {}).get(org_pid):
            if record.get("documentType") in config.get("types"):
                doc_pid = record.get("pid")
                try:
                    pid = PersistentIdentifier.create(
                        "urn",
                        doc_pid,
                        object_type="rec",
                        object_uuid=record.id,
                        status=PIDStatus.NEW,
                    )
                    urn_value = cls._generate_urn(int(pid.pid_value), config)
                    record["identifiedBy"].append(
                        {"type": "bf:Urn", "value": urn_value}
                    )
                except PIDAlreadyExists:
                    current_app.logger.error(
                        f'generated urn already exist for document: {doc_pid}')
