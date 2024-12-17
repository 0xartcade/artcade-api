"""Common serializers for reuse across apps"""

from rest_framework.serializers import CharField, ListField, Serializer, URLField


class AttributesSerializer(Serializer):
    trait_type = CharField()
    value = CharField()


class MetadataSerializer(Serializer):
    name = CharField()
    description = CharField(required=False)
    image = URLField()
    attributes = ListField(child=AttributesSerializer(), required=False)
