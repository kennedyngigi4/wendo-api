
from apps.blogs.models import Blog
from apps.blogs.serializers import BlogHomeSerializer

class BlogService:

    @staticmethod
    def home_blogs(request):
        queryset = Blog.objects.all().select_related(
            "category", "author"
        ).order_by("-published_at")

        serializer = BlogHomeSerializer(queryset, many=True, context={"request": request})

        return serializer.data

