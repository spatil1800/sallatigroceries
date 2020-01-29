# import logging
# import os
#
# import pytz
# from django.contrib import auth
# from django.contrib.auth import get_user_model
# from django.contrib.auth.password_validation import validate_password
# from django.contrib.auth.tokens import default_token_generator
# from django.core.exceptions import SuspiciousOperation
# from django.core.exceptions import ValidationError
# from django.http import HttpResponseRedirect
# from django.core.files.images import ImageFile
# from mozilla_django_oidc import views
# from rest_framework import status, generics
# from rest_framework.generics import CreateAPIView
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
# from rest_framework_jwt.views import ObtainJSONWebToken
#
# from common.filters import CustomSearchFilter
# from common.helpers import NoUnderscoreBeforeNumberCamelCaseJSONParser
# from pure_storage import utils
# from accounts.mails import send_activation_mail_to_user, send_password_reset_email
# from accounts.serializers import (
#     CreateUserSerializer,
#     PasswordResetSerializer,
#     JWTSerializer,
#     UserSerializer,
# )
# from pure_storage.accounts import auth
# from pure_storage.common import jwt_utils
# from jwt import exceptions
#
# from pure_storage.utils import get_or_none
# from pure_storage.accounts.services import UserService
#
# User = get_user_model()
# LOGGER = logging.getLogger(__name__)
#
#
# class SigninView(ObtainJSONWebToken):
#     serializer_class = JWTSerializer
#
#
# class SignupView(CreateAPIView):
#     """
#     Create User object
#     """
#
#     queryset = User.objects.none()
#     serializer_class = CreateUserSerializer
#     permission_classes = (AllowAny,)
#
#     def perform_create(self, serializer):
#         instance = serializer.save()
#         avatar = instance.avatar
#         if avatar.name == "":
#             name = instance.name.strip().split(" ")
#             if len(name) > 1:
#                 name = f"{name[0][0].upper()}{name[1][0].upper()}"
#             else:
#                 name = f"{name[0].upper()}"
#             file_path = UserService.generate_user_avatar(name)
#             basename = os.path.basename(file_path)
#             avatar = ImageFile(open(file_path, "rb"), name=basename)
#             instance.avatar = avatar
#             instance.save()
#             os.remove(file_path)
#
#
# class VerifyUserView(APIView):
#     permission_classes = (AllowAny,)
#
#     def get(self, request, uid, token, *args, **kwargs):
#         try:
#             uid = utils.decode_uid(uid)
#             user = User.objects.get(id=uid)
#         except (User.DoesNotExist, ValueError, TypeError, OverflowError):
#             return Response(
#                 status=status.HTTP_400_BAD_REQUEST, data={"message": "Invalid uid"}
#             )
#
#         is_token_valid = default_token_generator.check_token(user, token)
#         if not is_token_valid:
#             return Response(
#                 status=status.HTTP_400_BAD_REQUEST, data={"message": "Invalid token"}
#             )
#
#         user.is_active = True
#         user.save()
#
#         return Response(
#             status=status.HTTP_200_OK, data={"name": user.name, "email": user.email}
#         )
#
#
# class ResendVerifyUserView(APIView):
#     permission_classes = (AllowAny,)
#
#     def get(self, request, email, *args, **kwargs):
#         user = get_or_none(User, email=email)
#         if not user:
#             return Response(
#                 status=status.HTTP_404_NOT_FOUND, data={"email": "User doesn't exists"}
#             )
#         if user.is_active:
#             return Response(
#                 status=status.HTTP_400_BAD_REQUEST,
#                 data={"email": "User already active"},
#             )
#         send_activation_mail_to_user(user)
#         return Response(status=status.HTTP_200_OK)
#
#
# class PasswordResetView(APIView):
#     permission_classes = (AllowAny,)
#
#     def get(self, request, email, *args, **kwargs):
#         user = get_or_none(User, email=email)
#         if not user:
#             return Response(
#                 status=status.HTTP_404_NOT_FOUND, data={"email": "User doesn't exists"}
#             )
#         send_password_reset_email(user)
#         return Response(status=status.HTTP_200_OK)
#
#
# class PasswordResetFromKeyView(CreateAPIView):
#     permission_classes = (AllowAny,)
#     serializer_class = PasswordResetSerializer
#
#     def create(self, request, uid, token, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         try:
#             uid = utils.decode_uid(uid)
#             user = User.objects.get(id=uid)
#         except (User.DoesNotExist, ValueError, TypeError, OverflowError):
#             return Response(
#                 status=status.HTTP_400_BAD_REQUEST, data={"message": "Invalid uid"}
#             )
#
#         is_token_valid = default_token_generator.check_token(user, token)
#         if not is_token_valid:
#             return Response(
#                 status=status.HTTP_400_BAD_REQUEST, data={"message": "Invalid token"}
#             )
#
#         password = serializer.validated_data["password"]
#
#         try:
#             validate_password(password, user)
#         except ValidationError as e:
#             return Response(
#                 status=status.HTTP_400_BAD_REQUEST, data={"password": list(e.messages)}
#             )
#
#         user.set_password(password)
#         user.save()
#         return Response(
#             status=status.HTTP_200_OK, data={"name": user.name, "email": user.email}
#         )
#
#
# class TimezoneListAPIView(APIView):
#     permission_classes = ()
#
#     def get(self, request, format=None):
#         timezones = pytz.all_timezones
#         search_query = request.query_params.get("search", None)
#         if search_query:
#             filter_results = [k for k in timezones if search_query.lower() in k.lower()]
#         else:
#             filter_results = timezones
#         return Response(filter_results)
#
#
# class OIDCAuthenticationRequestView(views.OIDCAuthenticationRequestView):
#     def get(self, request):
#         request.session["next_page"] = request.GET["next_page"]
#         request.session["error_page"] = request.GET["error_page"]
#         response = super().get(request)
#
#         return response
#
#
# class OIDCAuthenticationCallbackView(views.OIDCAuthenticationCallbackView):
#     def get(self, request):
#         """Callback handler for OIDC authorization code flow"""
#
#         nonce = request.session.get("oidc_nonce")
#         if nonce:
#             # Make sure that nonce is not used twice
#             del request.session["oidc_nonce"]
#
#         if request.GET.get("error"):
#             # Ouch! Something important failed.
#             # Make sure the user doesn't get to continue to be logged in
#             # otherwise the refresh middleware will force the user to
#             # redirect to authorize again if the session refresh has
#             # expired.
#             # if is_authenticated(request.user):
#             #     auth.logout(request)
#             # assert not is_authenticated(request.user)
#             return Response(status=status.HTTP_401_UNAUTHORIZED)
#         elif "code" in request.GET and "state" in request.GET:
#             kwargs = {"request": request, "nonce": nonce}
#
#             if "oidc_state" not in request.session:
#                 # return self.login_failure()
#                 return Response(status=status.HTTP_401_UNAUTHORIZED)
#
#             if request.GET["state"] != request.session["oidc_state"]:
#                 msg = "Session `oidc_state` does not match the OIDC callback state"
#                 raise SuspiciousOperation(msg)
#
#             # Todo: Use below functions as auth.authenticate()
#             # self.user = auth.authenticate(**kwargs)
#             auth_backend = auth.OIDCAuthenticationBackend()
#             user = auth_backend.authenticate(**kwargs)
#
#             print(f"Authenticated User {user}")
#
#             if user:
#                 next_page = request.session["next_page"]
#                 payload = jwt_payload_handler(user)
#                 token = jwt_encode_handler(payload)
#                 return HttpResponseRedirect(f"{next_page}?token={token}")
#
#         # return self.login_failure()
#         return Response(status=status.HTTP_401_UNAUTHORIZED)
#
#
# class SignOutView(APIView):
#
#     def get(self, request):
#         try:
#             token = request.auth
#             LOGGER.debug(f'Input Token {token}')
#             jwt_utils.blacklist_jwt_token(token)
#         except exceptions.ExpiredSignatureError:
#             # Do nothing as token is already expired. Once the auth is enabled the request will never hit this code with
#             # expired token
#             pass
#         except exceptions.InvalidSignatureError:
#             return Response(
#                 status=status.HTTP_400_BAD_REQUEST, data={'message': 'Invalid Token'}
#             )
#         except Exception as e:
#             return Response(
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={'message': str(e)}
#             )
#
#         return Response(
#             status=status.HTTP_200_OK, data={"message": 'User is logged out successfully'}
#         )
#
#
# class UserListAPIView(generics.ListAPIView):
#     serializer_class = UserSerializer
#     queryset = User.objects.all()
#     permission_classes = (AllowAny,)
#     filter_backends = (CustomSearchFilter,)
#     search_fields = ["name", "email"]
#     parser_classes = (NoUnderscoreBeforeNumberCamelCaseJSONParser,)
#
#
# class UserRetrieveAPIView(generics.RetrieveAPIView):
#     serializer_class = UserSerializer
#     queryset = User.objects.all()
#     permission_classes = (AllowAny,)
#     parser_classes = (NoUnderscoreBeforeNumberCamelCaseJSONParser,)
