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

"""PDF extractor class."""

import os
import tempfile
import xml.etree.ElementTree as ET
from io import StringIO

import requests
import xmltodict
from flask import current_app


class PDFExtractor:
    """PDF extractor class."""

    api_url = ""

    def __init__(self):
        """Init PDF extractor."""
        self._load_config()

    def _load_config(self):
        """Load configuration from extension."""
        self.api_url = "http://{server}:{port}/api".format(
            server=current_app.config.get("PDF_EXTRACTOR_GROBID_SERVER"),
            port=current_app.config.get("PDF_EXTRACTOR_GROBID_PORT"),
        )
        if not self.api_is_alive():
            raise ConnectionRefusedError

    def api_is_alive(self):
        """Test if api is up.

        :returns: (bool) Return wether grobid service is up or not
        """
        try:
            response, status = self.do_request("isalive", "get")
        except Exception as err:
            return False

        if status != 200:
            return False

        return bool(response)

    def do_request(self, endpoint, request_type="get", files=None):
        """Do request on Grobid api.

        :param endpoint: (str) Endpoint of API to query
        :param request: (str) Request type (get or post)
        :param files: (dict) files to post (Multipart-encoded files)
        :returns: (tuple) Tuple containing response text and status
        """
        url = f"{self.api_url}/{endpoint}"

        if request_type.lower() not in ["get", "post"]:
            raise ValueError

        if request_type.lower() == "get":
            response = requests.get(url)
            return response.content, response.status_code

        if request_type.lower() == "post":
            headers = {"Accept": "application/xml"}
            response = requests.post(url, headers=headers, files=files)
            return response.text, response.status_code

    def process(self, input_file, output_file=None, dict_output=True):
        """Process metadata extraction from file.

        :param input_file: (str) Path to PDF file.
        :param output_file: (str) Output file where to dump extraction.
        :param dict_output: (bool) Extraction will be formatted in JSON.
        :returns: (str|dict|None) Metadata extraction, if output file is not
        None, data will be put into file
        """
        output = self.extract_metadata(input_file)

        # Dump xml output into given file
        if output_file:
            with open(output_file, "w") as file:
                file.write(output)
            return None

        # Return output as xml
        if not dict_output:
            return output

        # Transform xml to dictionary
        return self.parse_tei_xml(output)

    def process_raw(self, pdf_content, output_file=None, dict_output=True):
        """Metadata extraction from raw content.

        :param pdf_content: (str) PDF content.
        :param output_file: (str) Output file where to dump extraction.
        :param dict_output: (bool) Extraction will be formatted in JSON.
        :returns: (str|json) Metadata extraction
        """
        temp = tempfile.NamedTemporaryFile(mode="w+b", suffix=".pdf")
        temp.write(pdf_content)

        return self.process(temp.name, output_file=output_file, dict_output=dict_output)

    def extract_metadata(self, file):
        """Process metadata extraction.

        :param file: (str) Path to PDF file.
        :returns: (str) Extraction metadata as TEI XML
        """
        if not os.path.isfile(file):
            raise ValueError("Input file does not exist")

        if not file.lower().endswith(".pdf"):
            raise ValueError("Input file is not a valid PDF file")

        response, status = self.do_request(
            "processHeaderDocument",
            "post",
            files={
                "input": (file, open(file, "rb"), "application/pdf"),
                "consolidateHeader": 1,
            },
        )

        if status != 200:
            raise Exception("Metadata extraction failed")

        return response

    @staticmethod
    def parse_tei_xml(xml):
        """Parse xml content."""
        iterator = ET.iterparse(StringIO(xml))
        for _, element in iterator:
            if "}" in element.tag:
                element.tag = element.tag.split("}", 1)[1]
        root = iterator.root

        # parse xml
        result = xmltodict.parse(ET.tostring(root, encoding="unicode"))
        result = result["TEI"]

        return result
