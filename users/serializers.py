from rest_framework import serializers
from .models import User, Farms, Fields, Seasons, CropDataRotation, Jobs, FieldJobRecords


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','name','email','password']
        extra_kwargs = {
            'password':{'write_only':True}
        }


    def create(self,validated_data):
        password = validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
 
class FarmsSerializer(serializers.ModelSerializer):
    farm_id = serializers.CharField(read_only=True)
    class Meta:
        model = Farms
        fields = '__all__'

class SeasonsSerializer(serializers.ModelSerializer):
    season_id = serializers.CharField(read_only=True)
    class Meta:
        model = Seasons
        fields = '__all__'

class FieldsSerializer(serializers.ModelSerializer):
    field_id = serializers.CharField(read_only=True)
    class Meta:
        model = Fields
        fields = '__all__'

class JobsSerializer(serializers.ModelSerializer):
    job_id = serializers.CharField(read_only=True)
    class Meta:
        model = Jobs
        fields = '__all__'


class CropRotationSerializer(serializers.ModelSerializer):
    crop_rotation_id = serializers.CharField(read_only=True)
    class Meta:
        model = CropDataRotation
        fields = '__all__'


class FieldJobRecordsSerializer(serializers.ModelSerializer):
    field_job_record_id = serializers.CharField(read_only=True)
    class Meta:
        model = FieldJobRecords
        fields = '__all__'