from authentication.serializers import ChangePasswordSerializer, LoginSerializer, RegisterSerializer

from .models import User

from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser,IsAuthenticated




class RegisterView(generics.CreateAPIView,generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAdminUser,IsAuthenticated)
    serializer_class = RegisterSerializer




class AuthView(viewsets.GenericViewSet):
    """
        A viewset that provides the standard actions
    """
    queryset = User.objects.all()
    model = User

    def get_serializer_class(self):
        if self.action == 'change_password':
            return ChangePasswordSerializer
        elif self.action == 'login':
            return LoginSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['post'])
    def login(self, request):
        self.serializer_class = self.get_serializer_class()
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        is_valid = serializer.is_valid(raise_exception=False)
        if not is_valid:
            return Response("NO_USER", status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)

    @action(detail=False, methods=['put'])
    def change_password(self, request):
        user = request.user
        self.serializer_class = self.get_serializer_class()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid() and user.check_password(serializer.validated_data['old_password']):
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)