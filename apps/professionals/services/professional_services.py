from datetime import timedelta
from django.db.models import Max, Q, Avg, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.professionals.models.models import *
from apps.professionals.serializers.public_serializers import ProfessionalHomeSerializer
from apps.subscriptions.models.models import FeaturedSubscription
from apps.subscriptions.models.models import Plan, Subscription



class ProfessionalsServices:

    @staticmethod
    def featured_professionals(request, limit=10):
        queryset = Professional.objects.filter(
            is_active=True,
            user__is_active=True
        ).filter(
            Q(is_featured_manual=True) 
            # Q(featured_subscriptions__in=FeaturedSubscription.objects.active())
        ).prefetch_related(
            "operating_hours"
        ).annotate(
            avg_rating=Coalesce(Avg("reviews__rating"), Value(0.0))
        ).distinct().order_by(
            "-is_featured_manual",
            "-id"
        )[:limit]

        return ProfessionalHomeSerializer(
            queryset, many=True, context={"request": request}
        ).data
        
        # .annotate(
        #     max_priority=Max("featured_subscriptions__plan__priority")
        # ).prefetch_related(
        #     "featured_subscriptions__plan"
        # )


    #====================================================================
    #   PROFESSIONAL DASHBOARD
    #====================================================================
    @staticmethod
    def get_profile(professional, request):
        fields = [
            professional.name,
            professional.professional_type.name,
            professional.consultation_fee,
            professional.profile_photo,
            professional.location_name,
            professional.bio,
        ]

        completed = sum(1 for f in fields if f)
        total = len(fields)

        completion = int((completed / total) * 100)

        return {
            "name": professional.name,
            "profession": professional.professional_type.name,
            "photo": request.build_absolute_uri(professional.profile_photo.url) if professional.profile_photo else None,
            "consultation_fee": professional.consultation_fee,
            "location_name": professional.location_name,
            "completion": completion,
        }
    

    @staticmethod
    def get_upcoming_bookings(professional):
        bookings = professional.professional_bookings.order_by("-created_at")[:5]

        return [
            {
                "id": b.id,
                "user": b.name,
                "service": b.service.service.name,
                "appointment_date": b.appointment_date.strftime("%d %b"),
                "appointment_time": b.appointment_time.strftime("%I:%M %p"),
                "status": b.status,
            }
            for b in bookings
        ]

    @staticmethod
    def get_stats(professional):
        todays_appointments = professional.professional_bookings.filter(
            appointment_date=timezone.localdate(),
            status="confirmed"
        ).count()

        upcoming_appointments = professional.professional_bookings.filter(
            appointment_date__gte=timezone.now(),
        ).count()

        total_patients = professional.professional_bookings.filter(
            status="completed"
        ).values("email").distinct().count()

        reviews = professional.reviews.all()

        avg_rating = (
            sum(r.rating for r in reviews) / reviews.count()
            if reviews.exists() else 0
        )

        return {
            "todays_appointments": todays_appointments,
            "upcoming_appointments": upcoming_appointments,
            "total_patients": total_patients,
            "reviews_count": reviews.count(),
            "average_rating": round(avg_rating, 1),
        }
    

    @staticmethod
    def get_today_availability(professional):

        today = timezone.now().isoweekday()

        working_hours = professional.operating_hours.filter(
            day_of_week=today
        ).first()


        if not working_hours:
            return {
                "day_of_week": None,
                "message": "Please setup your working hours."
            }

        if working_hours.is_closed:
            return {
                "day_of_week": working_hours.day_of_week,
                "message": "Closed"
            }
        
        if working_hours.is_24:
            return {
                "day_of_week": working_hours.day_of_week,
                "message": "We are open 24 hours"
            }

        return {
            "day_of_week": working_hours.day_of_week,
            "message": f"We are open from {working_hours.open_time.strftime("%I:%M %p")} - {working_hours.close_time.strftime("%I:%M %p")}"
        }

    
    @staticmethod
    def get_reviews(professional):
        reviews = professional.reviews.order_by("-created_at")[:5]

        return [
            {
                "id": r.id,
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at,
            }
            for r in reviews
        ]


    @staticmethod
    def get_latest_subscription(professional):
        sub = professional.subscriptions.order_by("-created_at").first()

        if not sub:
            return {
                "is_active": False,
                "plan": None,
                "expires_at": None,
            }

        is_active = sub.end_date and sub.end_date > timezone.now()

        return {
            "id": sub.id,
            "plan": sub.plan.name,
            "status": sub.status,
            "is_active": is_active,
            "start_date": sub.start_date,
            "end_date": sub.end_date,
        }
    

    @staticmethod
    def get_subscription_capabilities(professional):
        sub = ProfessionalsServices.get_latest_subscription(professional)

        if not sub["is_active"]:
            return {
                "can_receive_bookings": False,
                "can_be_listed": False,
                "can_edit_profile": True,
            }

        return {
            "can_receive_bookings": True,
            "can_be_listed": True,
            "can_edit_profile": True,
        }
    

    @staticmethod
    def create_trial_subscription(professional):
        plan = Plan.objects.filter(is_trial=True, is_active=True, plan_for="professional").first()

        if not plan:
            return
        
        # Prevent duplicate trial subscriptions
        if Subscription.objects.filter(professional=professional, plan__is_trial=True).exists():
            return

        return Subscription.objects.create(
            user=professional.user,
            professional=professional,
            plan=plan,
            status="active",
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=plan.max_days),
            is_active=True
        )


