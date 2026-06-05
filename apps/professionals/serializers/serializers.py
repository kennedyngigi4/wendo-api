import json
from rest_framework import serializers

from apps.professionals.models.models import Professional, Specialty, Education, OperatingHours



class ProfessionalWriteSerializer(serializers.ModelSerializer): 
    specialties = serializers.PrimaryKeyRelatedField( queryset=Specialty.objects.all(), many=True, required=False ) 
    consultation_types = serializers.ListField( child=serializers.CharField(), required=False ) 
    
    class Meta: 
        model = Professional 
        fields = [ 
            "name", "title", "license_number", "bio", "professional_type", "specialties", 
            "years_of_experience", "consultation_fee", "gender", "phone", "email", "website", 
            "profile_photo", "country", "location_name", "latitude", "longitude",
            "consultation_types", "introduction_video_url", 
        ] 
        
    def to_internal_value(self, data): 

        print("REQUEST DATA:")
        print(data)


        mutable_data = data.copy() 
        consultation_types = (
            mutable_data.get("consultation_types") 
        ) 
        
        if (consultation_types and isinstance( consultation_types, str ) ): 
            try: 
                mutable_data[ "consultation_types" ] = json.loads( consultation_types ) 
            
            except json.JSONDecodeError: 
                pass 
            
        return super().to_internal_value( mutable_data ) 
    
    def create(self, validated_data): 
        specialties = validated_data.pop( "specialties", [] ) 
        professional = Professional.objects.create( **validated_data ) 
        professional.specialties.set( specialties ) 
        
        return professional 
    
    def update( self, instance, validated_data ): 
        
        specialties = validated_data.pop("specialties", None ) 
        
        for attr, value in validated_data.items(): 
            setattr( 
                instance, attr, value
            ) 
            
        instance.save() 
        
        if specialties is not None: 
            instance.specialties.set( 
                specialties 
            ) 
            
        return instance



class ProfessionalReadSerializer(serializers.ModelSerializer):

    specialties = serializers.SerializerMethodField()
    professional_type_name = serializers.StringRelatedField()
    profile_photo = serializers.SerializerMethodField()

    class Meta:
        model = Professional

        fields = [
            "id", "name", "title", "license_number", "bio", "years_of_experience", "consultation_fee", "gender", "phone",
            "email", "website", "profile_photo", "country", "location_name", "latitude", "longitude", 
            "consultation_types", "introduction_video_url", "professional_type", "professional_type_name", "specialties",
        ]

    def get_specialties(self, obj):

        return [
            {
                "id": spec.id,
                "name": spec.name
            }
            for spec in obj.specialties.all()
        ]
    

    def get_profile_photo(self, obj):
        request = self.context.get("request")
        if not obj.profile_photo:
            return None

        if request:
            return request.build_absolute_uri(
                obj.profile_photo.url
            )

        return obj.profile_photo.url



class ProfessionalWriteEducationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Education 
        fields = [
            "degree", "institution", "year_completed"
        ]


class ProfessionalReadEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education 
        fields = [
            "id", "degree", "institution", "year_completed"
        ]


class OperatingHoursItemSerializer(serializers.Serializer):

    day = serializers.IntegerField()

    from_time = serializers.CharField( required=False, allow_blank=True)
    to_time = serializers.CharField( required=False, allow_blank=True)

    is_closed = serializers.BooleanField(default=False)
    is_24 = serializers.BooleanField(default=False)

    def validate(self, attrs):

        is_closed = attrs.get("is_closed")
        is_24 = attrs.get("is_24")

        open_time = attrs.get("from_time")
        close_time = attrs.get("to_time")

        # Cannot be both
        if is_closed and is_24:
            raise serializers.ValidationError(
                "A day cannot be closed and 24 hours."
            )

        # Normal working day
        if not is_closed and not is_24:

            if not open_time:
                raise serializers.ValidationError({
                    "from_time": "Opening time is required."
                })

            if not close_time:
                raise serializers.ValidationError({
                    "to_time": "Closing time is required."
                })

        return attrs
    


class OperatingHoursBulkSerializer(serializers.Serializer):

    working_hours = OperatingHoursItemSerializer(many=True)

    def create(self, validated_data):

        professional = self.context["professional"]
        working_hours = validated_data["working_hours"]

        OperatingHours.objects.filter( professional=professional ).delete()

        objects = []

        for item in working_hours:

            is_closed = item.get("is_closed")
            is_24 = item.get("is_24")

            open_time = None
            close_time = None

            if not is_closed and not is_24:
                open_time = item.get("from_time")
                close_time = item.get("to_time")

            objects.append(
                OperatingHours(
                    professional=professional,
                    day_of_week=item["day"],
                    open_time=open_time,
                    close_time=close_time,
                    is_closed=is_closed,
                    is_24=is_24,
                )
            )

        return OperatingHours.objects.bulk_create(objects)




class OperatingHoursReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = OperatingHours
        fields = [
            "id",
            "day_of_week",
            "open_time",
            "close_time",
            "is_24",
            "is_closed",
        ]

