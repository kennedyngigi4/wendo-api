from datetime import timedelta
from django.db.models import Max, Q, Avg, Value, Sum, Count
from django.db.models.functions import Coalesce, TruncDate
from django.utils import timezone

from apps.bookings.models.models import Booking
from apps.professionals.models.models import Professional
from apps.providers.models.hospital_profile_models import ProviderBranch
from apps.providers.models.models import Provider
from apps.providers.serializers.public_serializers import ProviderBranchCardSerializer
from apps.subscriptions.models.models import FeaturedSubscription, Plan, Subscription



class ProvidersService:

    @staticmethod
    def featured_providers(request, limit=10):
        queryset = ProviderBranch.objects.filter(
            is_active=True,
            provider__is_active=True
        ).filter(
            Q(is_featured_manual=True) |
            Q(featured_subscriptions__in=FeaturedSubscription.objects.active())
        ).annotate(
            max_priority=Max("featured_subscriptions__plan__priority"),
            avg_rating=Coalesce(Avg("reviews__rating"), Value(0.0))
        ).select_related(
            "provider"
        ).prefetch_related(
            "operating_hours", "featured_subscriptions__plan"
        ).distinct().order_by(
            "-max_priority",
            "-is_featured_manual",
            "-id"
        )[:limit]


        return ProviderBranchCardSerializer(
            queryset, many=True, context={"request": request}
        ).data


    @staticmethod
    def create_branch_trial_subscription(branch):
        plan = Plan.objects.filter(is_trial=True, is_active=True, plan_for="provider").first()

        if not plan:
            return
        
        # Prevent duplicate trial subscriptions
        if Subscription.objects.filter(branch=branch, plan__is_trial=True).exists():
            return

        return Subscription.objects.create(
            user=branch.provider.owner,
            branch=branch,
            plan=plan,
            status="active",
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=plan.max_days),
            is_active=True
        )
    

    #==========================================================================
    #           MAIN PROVIDER DASHBOARD SERVICES
    #==========================================================================

    @staticmethod
    def get_provider_stats(user):
        total_companies = Provider.objects.filter(
            owner=user
        ).count()
        
        total_branches = ProviderBranch.objects.filter(
            provider__owner=user
        ).count()
        
        total_bookings = Booking.objects.filter(
            branch__provider__owner=user
        ).count()


        return {
            "total_companies": total_companies,
            "total_branches": total_branches,
            "total_bookings": total_bookings,
        }
    

    @staticmethod
    def get_provider_companies(user, request):
        companies = Provider.objects.filter(
            owner=user
        )
        return [
            {
                "id": c.id,
                "name": c.name,
                "is_active": c.is_active,
                "logo":  request.build_absolute_uri(c.logo.url) if c.logo else None,
                "provider_type": c.provider_type,
            }
            for c in companies
        ]
    

    @staticmethod
    def get_provider_branches(user):
        branches = ProviderBranch.objects.filter(
            provider__owner=user
        ).only("id", "name", "is_active", "is_main_branch", "is_verified")

        return [
            {
                "id": b.id,
                "name": b.name,
                "is_active": b.is_active,
                "is_main_branch": b.is_main_branch,
                "is_verified": b.is_verified,
                "provider": b.provider.name
            }

            for b in branches
        ]


    @staticmethod
    def get_provider_professional(user, request):
       
        professional = Professional.objects.filter(user=user).first()

        if professional:
            return {
                "id": professional.id,
                "name": professional.name,
                "title": professional.title,
                "created_at": professional.created_at,
                "is_active": professional.is_active,
                "is_verified": professional.is_verified,
                "profile_photo": request.build_absolute_uri(professional.profile_photo.url) if professional.profile_photo else None,
            }
        return None


    @staticmethod
    def get_provider_subscriptions(user):
        # providers = Provider.objects.filter(owner=user)
        branches = ProviderBranch.objects.filter(provider__owner=user)
        professionals = Professional.objects.filter(user=user)

        subscriptions = Subscription.objects.filter(
            Q(branch__in=branches) |
            Q(professional__in=professionals)
        ).select_related(
            "plan", "branch", "professional",
        ).order_by("-end_date")[:4]

        return [
            {
                "id": subscription.id,
                "plan": subscription.plan.name if subscription.plan else None,
                "status": subscription.status,
                "start_date": subscription.start_date,
                "end_date": subscription.end_date,
                "source": (
                    "branch" if subscription.branch else
                    "professional"
                ),
                "source_name": (
                    subscription.branch.name if subscription.branch else
                    subscription.professional.name
                ),
            }
            for subscription in subscriptions
        ]
        

    @staticmethod
    def get_all_subscriptions(user):
        # providers = Provider.objects.filter(owner=user)
        branches = ProviderBranch.objects.filter(provider__owner=user)
        professionals = Professional.objects.filter(user=user)

        subscriptions = Subscription.objects.filter(
            Q(branch__in=branches) |
            Q(professional__in=professionals)
        ).select_related(
            "plan", "branch", "professional",
        ).order_by("-end_date")

        return [
            {
                "id": subscription.id,
                "plan": subscription.plan.name if subscription.plan else None,
                "status": subscription.status,
                "start_date": subscription.start_date,
                "end_date": subscription.end_date,
                "source": (
                    "branch" if subscription.branch else
                    "professional"
                ),
                "source_name": (
                    subscription.branch.name if subscription.branch else
                    subscription.professional.name
                ),
            }
            for subscription in subscriptions
        ]



    #==========================================================================
    #           PROVIDER HOSPITAL/CLINIC DASHBOARD SERVICES
    #==========================================================================

    ## Main Dashboard stats

    @staticmethod 
    def get_stats(branch):
        total_bookings = branch.branch_bookings.count()
        patients_served = branch.branch_bookings.filter(
            status="completed"
        ).values("email").distinct().count()

        reviews = branch.reviews.all()
        avg_rating = (
            Sum(r.rating for r in reviews) / reviews.count()
            if reviews.exists() else 0
        )

        return {
            "total_bookings": total_bookings,
            "patients_served": patients_served,
            "avg_rating": avg_rating
        }


    @staticmethod
    def get_bookings_trend(branch):
        today = timezone.now().date()

        # 1. Create last 7 calendar days
        days = [
            today - timedelta(days=i)
            for i in reversed(range(7))
        ]

        # 2. Query actual bookings
        bookings = (
            branch.branch_bookings
            .filter(created_at__date__gte=days[0])
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(total=Count("id"))
        )

        # 3. Convert to lookup map
        bookings_map = {
            b["day"]: b["total"]
            for b in bookings
        }

        # 4. Build full series (fill missing with 0)
        return [
            {
                "date": day.strftime("%d %b"),
                "bookings": bookings_map.get(day, 0)
            }
            for day in days
        ]
    
    
    @staticmethod 
    def get_bookings_by_service(branch):
        services = branch.branch_bookings.values(
            "service__service__name"
        ).annotate(
            total=Count("id")
        ).order_by("-total")

        return [
            {
                "service": item["service__service__name"],
                "bookings": item["total"]
            }
            for item in services
        ]


    @staticmethod 
    def get_latest_subscription(branch):
        sub = branch.subscriptions.filter(
            is_active=True, 
        ).order_by("-created_at").first()

        if not sub:
            return {
                "is_active": False,
                "plan": None,
                "expires_at": None,
            }
        
        is_active = sub.end_date > timezone.now()

        return {
            "id": sub.id,
            "plan": sub.plan.name,
            "status": sub.status,
            "is_active": is_active,
            "start_date": sub.start_date,
            "end_date": sub.end_date,
        }


    @staticmethod 
    def get_recent_bookings(branch):
        latest_bookings = branch.branch_bookings.filter().order_by("-created_at")

        return [
            {
                "id": booking.id,
                "patient_name": booking.name,
                "service": booking.service.service.name,
                "status": booking.status,
                "date": booking.appointment_date.strftime("%d %b"),
                "time": booking.appointment_time.strftime("%I:%M %p"),
            }
            for booking in latest_bookings
        ]
    

    @staticmethod 
    def get_top_services(branch):
        top_services = branch.branch_services.annotate(
            total_bookings=Count("booking")
        ).order_by("-total_bookings")[:5]

        data = [ 
            {
                "id": service.id,
                "title": service.service.name,
                "bookings": service.total_bookings,
            }
            for service in top_services 
        ]

        return data


    @staticmethod 
    def get_latest_reviews(branch):
        latest_reviews = branch.reviews.order_by("-created_at")[:5]

        return [
            {
                "id": review.id,
                # "patient": review.name,
                "rating": review.rating,
                "comment": review.comment,
                "date": review.created_at.strftime("%d %b %Y"),
            }
            for review in latest_reviews
        ]

