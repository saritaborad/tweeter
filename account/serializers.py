from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str,force_str,smart_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.db.models import Q
from rest_framework import serializers



class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(label='Email Address')

    class Meta:
        model = User
        fields = ['username', 'email', 'password', ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        email = data['email']
        user_qs = User.objects.filter(email=email).exists()
        if user_qs:
            raise serializers.ValidationError('This user has already registered')
        return data

    def create(self, validated_data):
        print(validated_data)
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']
        user_obj = User.objects.create_user(username=username, email=email)
        user_obj.set_password(password)
        user_obj.save()
        return validated_data


class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(label='Email Address', required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        user_obj = None
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        user = User.objects.filter(Q(email=email) & Q(username=username)).distinct()
        if user.exists() and user.count() == 1:
            user_obj = user.first()
        else:
            raise serializers.ValidationError('Username or Email is invalid.')
        if user_obj:
            if not user_obj.check_password(password):
                raise serializers.ValidationError('password is incorrect')

        return data


class PasswrodResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8, write_only=True, required=True)
    token = serializers.CharField(write_only=True, required=True)
    uidb64 = serializers.CharField(write_only=True, required=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, data):
        try:
            password = data.get('passwrod ')
            token = data.get('token')
            uidb64 = data.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('The reset link is invalid', 401)
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            raise serializers.ValidationError('the reset link is invalid', 401)
        return super().validate(data)
