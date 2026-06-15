# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Dublin Core REST serializer."""

from invenio_records_rest.serializers.dc import (
    DublinCoreSerializer as BaseDublinCoreSerializer,
)
from lxml import etree

from .oai_dc import SonarDublinCoreXMLSerializer


class DublinCoreSerializer(BaseDublinCoreSerializer, SonarDublinCoreXMLSerializer):
    """Dublin Core REST serializer."""

    def serialize_object(self, obj):
        """Serialize a single object according to the response ctx."""

    def serialize(self, pid, record, links_factory=None):
        """Serialize a single record and persistent identifier.

        :param pid: Persistent identifier instance.
        :param record: Record instance.
        :param links_factory: Factory function for record links.
        """
        root = self.serialize_dict_to_etree(self.transform_record(pid, record, links_factory))
        return etree.tostring(root, pretty_print=True, encoding="UTF-8")

    def serialize_search(self, pid_fetcher, search_result, links=None, item_links_factory=None):
        """Serialize a search result.

        :param pid_fetcher: Persistent identifier fetcher.
        :param search_result: The search engine result.
        :param links: Dictionary of links to add to response.
        """
        root = etree.Element("collection", total=str(search_result["hits"]["total"]["value"]))
        for hit in search_result["hits"]["hits"]:
            child = self.serialize_dict_to_etree(
                self.transform_search_hit(
                    pid_fetcher(hit["_id"], hit["_source"]),
                    hit,
                    links_factory=item_links_factory,
                )
            )
            root.append(child)
        return etree.tostring(root, pretty_print=True, encoding="UTF-8")

    def dump(self, obj, context=None):
        """Serialize object with schema.

        Mandatory to override this method, as invenio-records-rest does not
        use the right way to dump objects (compatible with marshmallow 3.9).
        """
        return self.schema_class(context=context).dump(obj)
