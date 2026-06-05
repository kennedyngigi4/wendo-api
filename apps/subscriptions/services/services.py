from django.utils import timezone
from datetime import timedelta


from apps.subscriptions.models.models import Plan, Promotion, PromotionRedemption, Subscription



class SubscriptionService:


    @staticmethod
    def apply_trial_subscription(user, provider=None, professional=None):
        now = timezone.now()
        
        print("\n")

        print(user)
        print("\n")

        print(provider)
        print("\n")


        if provider:
            account_type = "provider"
        elif professional:
            account_type = "professional"
        else:
            return None
        

        # Get active trial promotion
        promo = Promotion.objects.filter(
            promo_type="trial",
            is_active=True,
            start_date__lte=now,
            end_date__gte=now,
        ).filter(
            apply_to__in=[account_type, "all"]
        ).first()


        print(promo)

        if not promo:
            return None

        if promo.is_first_time_only:
            already_used = PromotionRedemption.objects.filter(
                promotion=promo,
                user=user,
            ).exists()



            if already_used:
                return None
            
            
        plan = Plan.objects.filter(
            plan_for=account_type,
            is_active=True,
            is_free=True,
        ).first()

        print(plan)

        if not plan:
            return None
        
        end_date = now + timedelta(days=promo.free_days or plan.max_days)

        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            provider=provider,
            professional=professional,
            status="active",
            is_active=True,
            end_date=end_date
        )

        print(subscription)

        PromotionRedemption.objects.create(
            promotion=promo,
            user=user,
            provider=provider,
            professional=professional
        )

        return subscription



