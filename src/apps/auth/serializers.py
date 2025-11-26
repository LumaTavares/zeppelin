from django.contrib.auth.models import User
from rest_framework import serializers
from apps.employee.models import Employee
from rest_framework import generics, permissions

class RegistrarUsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    organization_name = serializers.CharField(required=False)  

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password','organization_name']
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Esse email já está cadastrado")
        return value

    def create(self, validated_data):
        organization_name = validated_data.pop('organization_name', None)
        password = validated_data.pop('password')
        validated_data['username'] = validated_data['email']
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    

class PasswordResetRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']


class PasswordResetConfirmSerializer(serializers.ModelSerializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)

    class Meta:
        model = User
        fields = ['uid', 'token', 'new_password']

class UserWithEmployeeSerializer(serializers.ModelSerializer):
    employee_data = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'organization_name']

    def get_employee_data(self, obj):
        try:
            # busca Employee pelo email do user
            employee = Employee.objects.get(e_mail=obj.email)
            return {
                'role': employee.role,
                'organization': employee.employee_organization.name if employee.employee_organization else None,
                'position': employee.employee_position.id if employee.employee_position else None
            }
        except Employee.DoesNotExist:
            return None
        
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['organization_name']
        extra_kwargs = {
            'organization_name': {'required': False}
        }
