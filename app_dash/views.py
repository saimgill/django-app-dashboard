from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import App, Plan, Subscription

from .serializers import AppSerializer, PlanSerializer, SubscriptionSerializer, UserSerializer
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

from django.shortcuts import get_object_or_404

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str 
from django.core.mail import send_mail
from django.conf import settings

@api_view(['POST'])
def login(request):
  user = get_object_or_404(User, username=request.data['username'])
  if not user.check_password(request.data['password']):
    return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
  token, created = Token.objects.get_or_create(user=user)
  return Response({'token': token.key, 'user': UserSerializer(user).data})

@api_view(['POST'])
def signup(request):
  serializer = UserSerializer(data=request.data)
  if serializer.is_valid():
    serializer.save()
    user = User.objects.get(username=request.data['username'])
    user.set_password(request.data['password'])
    user.save()
    token = Token.objects.create(user=user)
    return Response({'token': token.key, 'user': serializer.data})
  return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET']) 
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
  return Response('passed for {}'.format(request.user.email))

@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def app_list_create(request):
    if request.method == 'GET':
        apps = App.objects.filter(owner=request.user)
        serializer = AppSerializer(apps, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = AppSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def app_detail(request, pk):
    app = get_object_or_404(App, pk=pk, owner=request.user)
    
    if request.method == 'GET':
        serializer = AppSerializer(app)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = AppSerializer(app, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        app.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@api_view(['PUT'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def subscription_update(request, pk):
    subscription = get_object_or_404(Subscription, app_id=pk, app__owner=request.user)
    
    if request.method == 'PUT':
        plan_id = request.data.get('plan_id')
        if plan_id:
            try:
                new_plan = Plan.objects.get(id=plan_id)
                subscription.plan = new_plan
            except Plan.DoesNotExist:
                return Response({'detail': 'Invalid plan ID.'}, status=status.HTTP_400_BAD_REQUEST)

        if 'active' in request.data:
            subscription.active = request.data['active']

        subscription.save()
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)
    
    
@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def plan_list(request):
    if request.method == 'GET':
        plans = Plan.objects.all()
        serializer = PlanSerializer(plans, many=True)
        return Response(serializer.data)
    
@api_view(['POST'])
def password_reset_request(request):
    email = request.data.get('email')
    if not email:
        return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

    form = PasswordResetForm(data={'email': email})
    if not form.is_valid():
        return Response({"detail": "Invalid email."}, status=status.HTTP_400_BAD_REQUEST)
    
    users = User.objects.filter(email=email)
    for user in users:
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = request.build_absolute_uri(f'/password-reset-confirm/{uid}/{token}/')
        subject = "Password Reset Request"
        message = f"Hi {user.username},\n\nPlease use the following link to reset your password: {reset_link}\n\nIf you didn't request this, please ignore this email."
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

    return Response({"detail": "Password reset email sent."}, status=status.HTTP_200_OK)

@api_view(['POST'])
def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({"detail": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST)
    
    form = SetPasswordForm(user, data=request.data)
    if form.is_valid():
        form.save()
        return Response({"detail": "Password has been reset."}, status=status.HTTP_200_OK)
    
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)