# from django.urls import path
#
# from pure_storage.accounts.views import (
#     SignupView,
#     VerifyUserView,
#     PasswordResetView,
#     PasswordResetFromKeyView,
#     ResendVerifyUserView,
#     TimezoneListAPIView,
#     SigninView,
#     OIDCAuthenticationRequestView,
#     OIDCAuthenticationCallbackView,
#     UserListAPIView,
#     UserRetrieveAPIView,
#     SignOutView
# )
#
# app_name = "accounts"
# urlpatterns = [
#     path("signin", SigninView.as_view()),
#     path("signup", SignupView.as_view()),
#     path("signout", SignOutView.as_view()),
#
#     path("verify-user/<str:uid>/<str:token>", VerifyUserView.as_view()),
#     path("reverify-user/<str:email>", ResendVerifyUserView.as_view()),
#     path("password/reset/<str:email>", PasswordResetView.as_view()),
#     path(
#         "password/reset/key/<str:uid>/<str:token>", PasswordResetFromKeyView.as_view()
#     ),
#     path("timezones", TimezoneListAPIView.as_view(), name="timezone"),
#     path("oidc/okta/login", OIDCAuthenticationRequestView.as_view()),
#     path(
#         "oidc/okta/callback",
#         OIDCAuthenticationCallbackView.as_view(),
#         name="oidc_authentication_callback",
#     ),
#     path("users", UserListAPIView.as_view()),
#     path("users/<uuid:pk>", UserRetrieveAPIView.as_view()),
# ]
