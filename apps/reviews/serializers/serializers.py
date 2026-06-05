from rest_framework import serializers
from apps.reviews.models.models import Review



class ReviewWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = [
            "id", "rating", "comment", "created_at"
        ]


class ReviewReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = [
            "id", "rating", "comment", "created_at"
        ]
