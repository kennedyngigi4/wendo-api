from django.db.models import Q


from apps.blogs.models import Blog
from apps.professionals.models.models import Professional
from apps.providers.models.models import ProviderBranch


class SearchService:

    @staticmethod
    def search_specialists(query, request):

        query = query.strip()

        specialists = (
            Professional.objects.filter(is_active=True)
            .filter(
                Q(name__icontains=query) |
                Q(bio__icontains=query) |
                Q(professional_type__name__icontains=query) |
                Q(specialties__name__icontains=query) |
                Q(professional_services__service__name__icontains=query) |
                Q(professional_services__service__category__name__icontains=query)
            )
            .select_related("professional_type")
            .prefetch_related("specialties", "professional_services")
            .distinct()[:10]
        )

        return [
            {
                "id": item.id,
                "name": item.name,
                "specialty": item.professional_type.name if item.professional_type else None,
                "years_of_experience": item.years_of_experience,
                "consultation_fee": item.consultation_fee,
                "accepts_nhif": item.accepts_nhif,
                "profile_photo": request.build_absolute_uri(item.profile_photo.url) if item.profile_photo else None
            }
            for item in specialists
        ]


    @staticmethod
    def search_branches(query, request):
        branches = ProviderBranch.objects.filter(
            Q(name__icontains=query) 
            
    
            # Provider info
            # Q(provider__name__icontains=query) |
            # Q(provider__description__icontains=query) 

            # #Clinic Sessions
            # Q(clinic_sessions__title__icontains=query) |
            # Q(clinic_sessions__description__icontains=query) |

            # # Services
            # Q(branch_services__service__name__icontains=query) |

            # # Service Categories
            # Q(branch_services__service__category__name__icontains=query) |

            # # Specialties
            # Q(branch_services__specialties__name__icontains=query) |

            # # Professionals attached to services
            # Q(branch_services__professional__specialties__name__icontains=query)

        ).select_related(
            "provider"
        ).prefetch_related(
            "branch_services",
            "clinic_sessions"
        ).distinct()[:10]

        return [
                {
                    "id": item.id,
                    "name": item.name,
                    "type": item.provider.provider_type,
                    "location_name": item.location,
                    "phone": item.phone,
                    "banner": request.build_absolute_uri(item.provider.banner.url) if item.provider.banner else None
                }
                for item in branches
        ]


    @staticmethod
    def search_blogs(query):
        blogs = Blog.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )[:8]

        return [
            {
                "id": item.id,
                "title": item.title,
                "slug": item.slug,
                "published_at": item.published_at,
                "author": item.author
            }
            for item in blogs
        ]




