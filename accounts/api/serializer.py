from rest_framework import serializers

from accounts.models import User, Profile, Groups, Region, Area, ClassRoom


class UserModelSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=30)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=30)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name')


# *********************************************

class PClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoom
        fields = ('id', 'name')


class PAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ('id', 'name')


class PRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('id', 'name')


class PGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Groups
        fields = ('id', 'name', 'description')


class ProfileModelSerializer(serializers.ModelSerializer):
    user = UserModelSerializer()
    classroom = PClassSerializer(read_only=True)
    related_area = PAreaSerializer(read_only=True)
    related_region = PRegionSerializer(read_only=True)

    group = PGroupSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = (
            'id', 'user', 'group', 'classroom', 'related_area', 'related_region',
            'is_student', 'is_teacher', 'is_executive', 'is_admin'
        )
        read_only_fields = ('is_student', 'is_teacher', 'is_executive', 'is_admin',)

    def update(self, instance, validated_data):
        validated_user = validated_data.get('user')
        if validated_user:
            u = User.objects.get(profile=instance)
            u.username = validated_user.get('username', u.username)
            if validated_user.get('password', None):
                u.set_password(validated_user.get('password'))

            u.first_name = validated_user.get('first_name', u.first_name)
            u.last_name = validated_user.get('last_name', u.last_name)
            u.save()

        instance.save()
        return instance


class AdminProfileModelSerializer(serializers.ModelSerializer):
    user = UserModelSerializer()
    classroom = PClassSerializer()
    related_area = PAreaSerializer()
    related_region = PRegionSerializer(read_only=True)

    group = PGroupSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = (
            'id', 'user', 'group', 'classroom', 'related_area', 'related_region',
            'is_student', 'is_teacher', 'is_executive', 'is_admin'
        )

    def validate(self, attrs):
        if attrs.get('is_student', False) or attrs.get('is_teacher', False):
            if not attrs.get('classroom', None):
                raise serializers.ValidationError("classroom filed cannot be blank")
            if attrs['classroom'].related_area != attrs['related_area']:
                raise serializers.ValidationError("classroom not in related area")
            if attrs['related_area'].related_region != attrs['related_region']:
                raise serializers.ValidationError("related area not in related region")

        if attrs.get('is_executive', False):
            if not attrs.get('related_area', None):
                raise serializers.ValidationError("related_area filed cannot be blank")
            if attrs['related_area'].related_region != attrs['related_region']:
                raise serializers.ValidationError("related area not in related region")

        ###
        # buraya ekstra kontroller koyulaması gerekiyor ......
        ###
        return attrs


class AdminProfileCreateSerializer(AdminProfileModelSerializer):
    classroom = serializers.PrimaryKeyRelatedField(required=False, queryset=ClassRoom.objects.all())
    related_area = serializers.PrimaryKeyRelatedField(required=False, queryset=Area.objects.all())
    related_region = serializers.PrimaryKeyRelatedField(required=True, queryset=Region.objects.all())
    group = serializers.PrimaryKeyRelatedField(required=False, queryset=Groups.objects.all())

    def create(self, validated_data):
        u = validated_data['user']
        password = u.pop('password')

        user = User(**u)  # new user create
        user.set_password(password)
        user.save()

        current_user = self.context['current_user']

        pr = Profile(user=user, created_by=current_user)

        pr.group = self.validated_data['group']

        # student bir sınıfa aittir
        pr.is_student = validated_data.get('is_student', False)
        if pr.is_student:
            pr.classroom = validated_data['classroom']
            pr.related_area = validated_data['related_area']

        # teacher bir sınıfa ait değildir
        pr.is_teacher = validated_data.get('is_teacher', False)
        if pr.is_teacher:
            validated_data['classroom'].teachers.add(user)
            pr.related_area = validated_data['related_area']

        # executive areaya ait değildir
        pr.is_executive = validated_data.get('is_executive', False)
        if pr.is_executive:
            validated_data['related_area'].executives.add(user)

        # admin daha sonra düşünülecek ****
        # pr.is_admin = validated_data.get('is_admin', False)
        pr.related_region = validated_data['related_region']

        pr.save()
        return pr


class AdminProfileUpdateSerializer(AdminProfileCreateSerializer):
    user = UserModelSerializer(required=False)
    related_region = serializers.PrimaryKeyRelatedField(required=False, queryset=Region.objects.all())

    def update(self, instance, validated_data):
        instance.is_student = validated_data.get('is_student', instance.is_student)
        instance.is_teacher = validated_data.get('is_teacher', instance.is_teacher)
        instance.is_executive = validated_data.get('is_executive', instance.is_executive)
        # instance.is_admin = validated_data.get('is_admin', instance.admin)

        instance.group = validated_data.get('group', instance.group)

        instance.classroom = validated_data.get('classroom', instance.classroom)
        instance.related_area = validated_data.get('related_area', instance.classroom)
        instance.related_region = validated_data.get('related_region', instance.classroom)

        # student bir sınıfa aittir

        if validated_data.get('is_student', False):
            instance.is_student = True
            instance.classroom = validated_data['classroom']
            instance.related_area = validated_data['related_area']

        # teacher bir sınıfa ait değildir, ama bölgeye aittir
        if validated_data.get('is_teacher', False):
            instance.is_teacher = True
            validated_data['classroom'].teachers.add(instance.user)
            instance.related_area = validated_data['related_area']

        # executive areaya ait değildir
        if validated_data.get('is_executive', False):
            instance.is_executive = True
            validated_data['related_area'].executives.add(instance.user)

        validated_user = validated_data.get('user')
        if validated_user:
            u = User.objects.get(profile=instance)
            u.username = validated_user.get('username', u.username)
            u.password = validated_user.get('password', u.password)

            u.first_name = validated_user.get('first_name', u.first_name)
            u.last_name = validated_user.get('last_name', u.last_name)
            u.save()

        instance.save()
        return instance
