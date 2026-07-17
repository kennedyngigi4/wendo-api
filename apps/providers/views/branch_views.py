from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Max, Min, Q
from django.core.cache import cache


from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.accounts.permissions import IsProvider
from apps.providers.services.branch_service import BranchService
from apps.providers.services.hospital_service import HospitalProfileService
from apps.providers.serializers.branch_serializers import BranchWriteSerializer, BranchListSerializer, BranchDetailSerializer, HospitalProfileUpdateSerializer, BranchUpdateSerializer


class BranchesViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated, IsProvider]
    serializer_class = BranchListSerializer

    def get_queryset(self):
        return BranchService.get_branches(self.request.user)
    
    def get_serializer_class(self):
        if self.action == "create":
            return  BranchWriteSerializer
        
        if self.action in [ "update", "partial_update"]:
            return  BranchWriteSerializer
        
        if self.action == "hospital_profile":
            return HospitalProfileUpdateSerializer
        
        if self.action == "retrieve":
            return BranchDetailSerializer
        
        if self.action == "list":
            return BranchListSerializer
        
        return BranchWriteSerializer


    @action(detail=True, methods=["patch"], url_path="hospital_profile")
    def hospital_profile(self, request, pk=None):

        serializer = self.get_serializer(
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        HospitalProfileService.update_profile(
            user=self.request.user,
            branch_id=pk,
            **serializer.validated_data
        )

        return Response({
            "success": True,
            "message": "Hospital profile updated."
        })


    def create(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            
            branch = BranchService.create_branch(
                user=self.request.user, 
                **serializer.validated_data
            )
            return Response({ "success": True, "message": "Branch created.", "id": branch.id}, status=status.HTTP_201_CREATED)
    
        
        return Response({ "success": False, "message": "Something went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def retrieve(self, request, *args, **kwargs):
        
        user = self.request.user
        
        branch = BranchService.get_branch(
            self.request.user,
            kwargs["pk"]
        )

        serializer = self.get_serializer(branch)
        return Response({
            "success": True,
            "data": serializer.data
        })


    def partial_update(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        branch = BranchService.update_branch(
            self.request.user,
            kwargs["pk"],
            **serializer.validated_data
        )

        return Response(
            {
                "success": True,
                "message": "Branch updated.",
                "data": BranchListSerializer(branch).data
            }
        )


    def destroy(self, request, *args, **kwargs):

        BranchService.delete_branch(
            request.user,
            kwargs["pk"]
        )

        return Response(
            {
                "success": True,
                "message": "Branch deleted."
            },
            status=status.HTTP_204_NO_CONTENT,
        )



