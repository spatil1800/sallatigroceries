import pytz
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework_jwt.compat import PasswordField
from rest_framework_jwt.serializers import (
    JSONWebTokenSerializer,
    jwt_payload_handler,
    jwt_encode_handler,
)

User = get_user_model()


class JWTSerializer(JSONWebTokenSerializer):
    def __init__(self, *args, **kwargs):
        """
        Dynamically add the USERNAME_FIELD to self.fields.
        """
        super(JSONWebTokenSerializer, self).__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.EmailField()
        self.fields["password"] = PasswordField(write_only=True)

    @property
    def username_field(self):
        return "email"

    def validate(self, attrs):
        credentials = {
            self.username_field: attrs.get(self.username_field),
            "password": attrs.get("password"),
        }
        try:
            user_object = User.objects.get(email=credentials.get("email"))
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"password": ["Incorrect authentication credentials."]}
            )

        if not user_object.is_active:
            raise serializers.ValidationError({"email": ["User is not active"]})

        if all(credentials.values()):
            user = authenticate(request=self.context["request"], **credentials)

            if user:
                if not user.is_active:
                    msg = _("User account is disabled.")
                    raise serializers.ValidationError(msg)

                payload = jwt_payload_handler(user)

                return {"token": jwt_encode_handler(payload), "user": user}
            else:
                raise serializers.ValidationError(
                    {"password": ["Incorrect authentication credentials."]}
                )
        else:
            msg = _('Must include "{username_field}" and "password".')
            msg = msg.format(username_field=self.username_field)
            raise serializers.ValidationError(msg)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "name")
        read_only_fields = ("email",)


class CreateUserSerializer(serializers.ModelSerializer):
    timezone = serializers.ChoiceField(
        choices=tuple(zip(pytz.all_timezones, pytz.all_timezones)), default="UTC"
    )
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    def create(self, validated_data):
        # call create_user on user object. Without this
        # the password will be stored in plain text.
        user = User.objects.create_user(**validated_data)
        # TODO: Send activation email to the new created User
        # send_activation_mail_to_user(user)
        return user

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    class Meta:
        model = User
        fields = ("id", "name", "email", "password", "timezone", "avatar")
        write_only_fields = ("password",)


class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
