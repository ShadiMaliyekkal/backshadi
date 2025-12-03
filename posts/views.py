from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer, LikeSerializer, UserSerializer  # optional import if you made one
from .permissions import IsOwnerOrReadOnly

User = get_user_model()

class PostViewSet(viewsets.ModelViewSet):
    """
    Public can list/retrieve posts.
    Only authenticated users can create posts.
    Only owners can update/delete (IsOwnerOrReadOnly).
    """
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = Like.objects.get_or_create(post=post, user=request.user)
        if created:
            return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)
        else:
            like.delete()
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Comments are visible publicly but only authenticated users can create.
    Only owners can edit/delete their comments.
    """
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        # If you allow creating comments through /comments/ endpoint
        serializer.save(author=self.request.user)


class LikeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only listing of likes. Toggling likes is handled on PostViewSet.like action.
    """
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# --------- Registration / auth helper endpoints ---------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        return user


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    ser = RegisterSerializer(data=request.data)
    if ser.is_valid():
        user = ser.save()
        return Response({'id': user.id, 'username': user.username}, status=status.HTTP_201_CREATED)
    return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    Return current logged-in user's basic info.
    Frontend can call GET /api/auth/user/ with Authorization header.
    """
    # A simple lightweight serializer for the user
    return Response({
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
    })
