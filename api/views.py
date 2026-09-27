from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Q
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import KBEntry, QueryLog
from .permissions import IsAdminUser
from .serializers import LoginSerializer, RegistrationSerializer


def access_token_for(user):
    return str(RefreshToken.for_user(user).access_token)


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
            email=serializer.validated_data['email'],
        )
        company = user.company
        company.company_name = serializer.validated_data['company_name']
        company.save(update_fields=['company_name'])
        return Response({
            'username': user.username,
            'company_name': company.company_name,
            'api_key': company.api_key,
            'access': access_token_for(user),
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )
        if user is None or not hasattr(user, 'company'):
            return Response({'detail': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)
        company = user.company
        return Response({
            'access': access_token_for(user),
            'company_name': company.company_name,
            'api_key': company.api_key,
        })


class KBQueryView(APIView):
    def post(self, request):
        search_term = request.data.get('search')
        if not isinstance(search_term, str) or not search_term.strip():
            return Response({'search': ['This field is required and cannot be blank.']}, status=status.HTTP_400_BAD_REQUEST)
        search_term = search_term.strip()
        with transaction.atomic():
            entries = list(KBEntry.objects.filter(
                Q(question__icontains=search_term) | Q(answer__icontains=search_term)
            ))
            QueryLog.objects.create(
                company=request.user.company,
                search_term=search_term,
                results_count=len(entries),
            )
        return Response({
            'search': search_term,
            'count': len(entries),
            'results': [
                {'id': str(entry.id), 'question': entry.question, 'answer': entry.answer, 'category': entry.category}
                for entry in entries
            ],
        })


class UsageSummaryView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_queries = QueryLog.objects.aggregate(total=Count('id'))['total'] or 0
        active_companies = QueryLog.objects.values('company').distinct().count()
        top_search_terms = QueryLog.objects.values('search_term').annotate(count=Count('id')).order_by('-count')[:5]
        return Response({
            'total_queries': total_queries,
            'active_companies': active_companies,
            'top_search_terms': list(top_search_terms),
        })
