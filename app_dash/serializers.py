from rest_framework import serializers
from django.contrib.auth.models import User

from .models import App, Plan, Subscription

class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ('id', 'username', 'password', 'email')
    
class AppSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = App
        fields = ('id', 'name', 'description', 'owner', 'created_at', 'updated_at')

    def create(self, validated_data):
        app = App.objects.create(**validated_data)
        free_plan = Plan.objects.get(name='Free')
        Subscription.objects.create(app=app, plan=free_plan)
        return app

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ('id', 'name', 'price')

class SubscriptionSerializer(serializers.ModelSerializer):
    app = serializers.ReadOnlyField(source='app.name')
    plan = serializers.ReadOnlyField(source='plan.name')

    class Meta:
        model = Subscription
        fields = ('id', 'app', 'plan', 'active', 'start_date', 'end_date')

    def update(self, instance, validated_data):
        instance.active = validated_data.get('active', instance.active)
        instance.save()
        return instance