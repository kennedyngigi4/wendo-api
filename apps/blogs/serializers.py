from rest_framework import serializers
from apps.blogs.models import Blog, BlogCategory



class BlogCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = BlogCategory
        fields = [
            "id", "name"
        ]



class BlogHomeSerializer(serializers.ModelSerializer):

    image = serializers.SerializerMethodField()
    author = serializers.CharField(source="author.fullname", read_only=True)

    class Meta:
        model = Blog
        fields = [
            "id", "slug", "title", "image", "exerpt", "author", "published_at"
        ]


    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None




class BlogDetailSerializer(serializers.ModelSerializer):
    
    category = serializers.CharField(source="category.name", read_only=True)
    image = serializers.SerializerMethodField()
    author = serializers.CharField(source="author.fullname", read_only=True)
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = [
            "id",
            "title",
            "slug",
            "category",
            "image",
            "exerpt",
            "content",
            "tags",
            "author",
            "published_at",
        ]

    def get_tags(self, obj):
        if not obj.tags:
            return []
        return [tag.strip() for tag in obj.tags.split(",")]

    def get_image(self, obj):
        request = self.context.get("request")

        if not obj.image:
            return None

        if request:
            return request.build_absolute_uri(obj.image.url)

        return obj.image.url


