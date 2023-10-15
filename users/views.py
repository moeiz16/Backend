from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework import status
from .serializers import UserSerializer, FarmsSerializer, SeasonsSerializer, FieldsSerializer, JobsSerializer, CropRotationSerializer, FieldJobRecordsSerializer
from .models import User, Farms, Seasons, Fields, Jobs, CropDataRotation, FieldJobRecords
import jwt
import datetime
import ast
import math
from flask import request
# Create your views here.


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        current_year = datetime.date.today().year
        start_date = f"{current_year}-01-01"

        end_date = f"{current_year}-03-01"
        season_name = f"Spring {current_year}"
        season_data = {
            'user': serializer.data['id'],
            'start_date': start_date,
            'end_date': end_date,
            'season_name': season_name
        }

        farm_data = {
            'user': serializer.data['id'],
            'location': "{'lat': 31.474943738576684, 'lng': 73.99439415589569}",
            'farm_name': 'Farm 1'

        }
        seasons_data = []
        farms_data = []
        # Serialize the data
        season_serializer = SeasonsSerializer(data=season_data)

        # Validate the serializer
        if season_serializer.is_valid():
            # Save the farm record
            season_serializer.save()
            print(season_serializer.data)
            seasons_data.append(season_serializer.data)

            # Serialize the data
        farm_serializer = FarmsSerializer(data=farm_data)

        # Validate the serializer
        if farm_serializer.is_valid():
            # Save the farm record
            farm_serializer.save()
            farms_data.append(farm_serializer.data)

        response = Response()
        response.data = {
            'id': serializer.data['id'],
            'name': serializer.data['name'],
            'email': serializer.data['email'],
            'seasons': seasons_data,
            'farms': farms_data
        }

        return response


class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['mypassword']
        print(email)

        user = User.objects.filter(email=email).first()
        print(user)
        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect Password!')

        jwt_exp_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

        payload = {
            'id': user.id,
            'exp': jwt_exp_time,
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')
        # Fetch the user's fields and serialize them
        farms = Farms.objects.filter(user=user)
        # Assuming you have a FieldSerializer
        farm_serializer = FarmsSerializer(farms, many=True)

        seasons = Seasons.objects.filter(user=user)
        # Assuming you have a FieldSerializer
        season_serializer = SeasonsSerializer(seasons, many=True)

        fields = Fields.objects.filter(
            farm_id_id=farm_serializer.data[0]['farm_id'])
        field_serializer = FieldsSerializer(fields, many=True)

        crop_rotation_records = CropDataRotation.objects.filter(
            season_id_id=season_serializer.data[0]['season_id'])
        crop_rotation_serializer = CropRotationSerializer(
            crop_rotation_records, many=True)

        job_records = Jobs.objects.filter(
            season_id_id=season_serializer.data[0]['season_id'], farm_id_id=farm_serializer.data[0]['farm_id'])
        job_serializer = JobsSerializer(
            job_records, many=True)
        response = Response()

        response.set_cookie(key='jwt', value=token,
                            httponly=True, expires=jwt_exp_time)
        response.data = {

            'userid': user.id,
            'username': user.name,
            'email': user.email,
            'jwt': token,
            'farms': farm_serializer.data,
            'seasons': season_serializer.data,
            'fields': field_serializer.data,
            'crop_rotation_records': crop_rotation_serializer.data,
            'jobs': job_serializer.data
        }

        # Check if the JWT has expired in a request
        if 'jwt' in request.cookies:
            jwt_token = request.cookies['jwt']
            try:
                payload = jwt.decode(jwt_token, 'secret', algorithms=['HS256'])
                exp_time = datetime.datetime.utcfromtimestamp(payload['exp'])
                current_time = datetime.datetime.utcnow()
                if current_time >= exp_time:
                    # JWT has expired, so delete the cookie
                    response.delete_cookie('jwt')
            except jwt.ExpiredSignatureError:
                # JWT has expired, so delete the cookie
                response.delete_cookie('jwt')

        return response


class UserView(APIView):

    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)

        return Response(serializer.data)


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response


class CreateFarmView(APIView):
    def post(self, request):
        # Extract data from the request
        user = User.objects.filter(email=request.data['email']).first()
        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(request.data['password']):
            raise AuthenticationFailed('Incorrect Password!')

        data = {
            'user': user.id,
            'farm_name': request.data['farm_name'],
            'location': str(request.data['location'])
        }
        # Serialize the data
        serializer = FarmsSerializer(data=data)

        # Validate the serializer
        if serializer.is_valid():
            # Save the farm record
            serializer.save()
            farms = Farms.objects.filter(user=user)
            # Assuming you have a FieldSerializer
            farm_serializer = FarmsSerializer(farms, many=True)
            response = Response()
            response.data = {
                'farms': farm_serializer.data
            }
            return response
        # If the serializer is not valid, return an error response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateSeasonView(APIView):
    def post(self, request):
        # Extract data from the request
        user = User.objects.filter(email=request.data['email']).first()
        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(request.data['password']):
            raise AuthenticationFailed('Incorrect Password!')

        data = {
            'user': user.id,
            'start_date': request.data['start_date'],
            'end_date': request.data['end_date'],
            'season_name': request.data['season_name']
        }
        # Serialize the data
        serializer = SeasonsSerializer(data=data)

        # Validate the serializer
        if serializer.is_valid():
            # Save the farm record
            serializer.save()

            seasons = Seasons.objects.filter(user=user)
            # Assuming you have a FieldSerializer
            season_serializer = SeasonsSerializer(seasons, many=True)
            response = Response()
            response.data = {
                'seasons': season_serializer.data
            }
            return response
        # If the serializer is not valid, return an error response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateFieldView(APIView):
    def post(self, request):
        # Extract data from the request

        farm = Farms.objects.filter(farm_id=request.data['farm_id']).first()
        if farm is None:
            raise NotFound('Farm not found!')
        print(request.data)
        data = {
            'farm_id': farm.farm_id,
            'coordinates': str(request.data['coordinates']),
            'field_name': request.data['field_name'],
            'area': request.data['area'],
            'description': request.data['description']
        }

        # Serialize the data
        serializer = FieldsSerializer(data=data)

        # Validate the serializer
        if serializer.is_valid():
            # Save the farm record
            serializer.save()

            # Respond with a success message
            fields = Fields.objects.filter(farm_id_id=farm.farm_id)
            field_serializer = FieldsSerializer(fields, many=True)

            response = Response({
                'fields': field_serializer.data,
            })
            return response

        # If the serializer is not valid, return an error response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateJobView(APIView):
    def post(self, request):
        # Extract data from the request
        farm = Farms.objects.filter(farm_id=request.data['farm_id']).first()
        print(farm)
        if farm is None:
            raise NotFound('Farm not found!')
        season = Seasons.objects.filter(
            season_id=request.data['season_id']).first()
        if season is None:
            raise NotFound('Season not found!')

        data = {
            'farm_id': farm.farm_id,
            'season_id': season.season_id,
            'field_job_type': request.data['field_job_type'],
            'due_date': request.data['due_date']

        }
        # Serialize the data
        serializer = JobsSerializer(data=data)

        # Validate the serializer
        if serializer.is_valid():
            # Save the farm record
            serializer.save()

            # Respond with a success message
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # If the serializer is not valid, return an error response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateCropRotationView(APIView):
    def post(self, request):
        # Extract data from the request
        field = Fields.objects.filter(
            field_id=request.data['field_id']).first()
        print(field.field_id)
        if field is None:
            raise NotFound('Field not found!')
        season = Seasons.objects.filter(
            season_id=request.data['season_id']).first()
        if season is None:
            raise NotFound('Season not found!')

        data = {
            'field_id': field.field_id,
            'season_id': season.season_id,
            'crop_type': request.data['crop_type'],
            'sown_date': request.data['sown_date'],
            'harvest_date': request.data['harvest_date']

        }
        # Serialize the data
        serializer = CropRotationSerializer(data=data)

        # Validate the serializer
        if serializer.is_valid():
            # Save the farm record
            serializer.save()

            crop_rotation_records = CropDataRotation.objects.filter(
                season_id_id=season.season_id)
            crop_rotation_serializer = CropRotationSerializer(
                crop_rotation_records, many=True)

            response = Response()

            response.data = {
                'crop_rotation_records': crop_rotation_serializer.data
            }
            return response

        # If the serializer is not valid, return an error response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateFieldJobRecordView(APIView):
    def post(self, request):
        # Extract data from the request
        field = Fields.objects.filter(
            field_id=request.data['field_id']).first()
        if field is None:
            raise NotFound('Field not found!')
        job = Jobs.objects.filter(job_id=request.data['job_id']).first()
        if job is None:
            raise NotFound('Job not found!')

        data = {
            'field_id': field.field_id,
            'job_id': job.job_id,
            'status': request.data['status'],


        }
        # Serialize the data
        serializer = FieldJobRecordsSerializer(data=data)

        # Validate the serializer
        if serializer.is_valid():
            # Save the farm record
            serializer.save()

            # Respond with a success message
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # If the serializer is not valid, return an error response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DisplayFieldsbyFarmView(APIView):
    def post(self, request, farm_id):

        fields = Fields.objects.filter(farm_id_id=farm_id)
        field_serializer = FieldsSerializer(fields, many=True)

        job_records = Jobs.objects.filter(
            season_id_id=request.data['season_id'], farm_id_id=farm_id)
        job_serializer = JobsSerializer(
            job_records, many=True)

        response = Response()

        response.data = {
            'fields': field_serializer.data,
            'jobs': job_serializer.data
        }

        return response


class UpdateFieldView(APIView):
    def put(self, request, field_id):

        print(request.data)
        farm_id = request.data['farm_id']
        coordinates = request.data['coordinates']
        area = request.data['area']
        description = request.data['field_description']
        name = request.data['field_name']

        farm = Farms.objects.filter(farm_id=farm_id).first()

        if farm is None:
            raise NotFound('No such farm')

        try:
            field = Fields.objects.get(field_id=field_id, farm_id=farm)
        except Fields.DoesNotExist:
            raise NotFound('Field not found')

        field.coordinates = coordinates
        field.area = area
        field.description = description
        field.field_name = name
        field.save()

        fields = Fields.objects.filter(farm_id=farm)
        field_serializer = FieldsSerializer(fields, many=True)
        response = Response({
            'fields': field_serializer.data,
        })

        return response


class DeleteFieldView(APIView):
    def delete(self, request, field_id):
        farm_id = request.data['farm_id']
        farm = Farms.objects.filter(farm_id=farm_id).first()

        if farm is None:
            raise NotFound('No such farm')
        try:
            field = Fields.objects.get(field_id=field_id, farm_id=farm)
        except Fields.DoesNotExist:
            raise NotFound('Field not found')

        field.delete()
        fields = Fields.objects.filter(farm_id=farm)
        field_serializer = FieldsSerializer(fields, many=True)
        response = Response({
            'fields': field_serializer.data,
        })

        return response


class DisplaySeasonCropRotationDataView(APIView):
    def post(self, request, season_id):
        crop_rotation_records = CropDataRotation.objects.filter(
            season_id_id=season_id)
        crop_rotation_serializer = CropRotationSerializer(
            crop_rotation_records, many=True)

        job_records = Jobs.objects.filter(
            season_id_id=season_id, farm_id_id=request.data['farm_id'])
        job_serializer = JobsSerializer(
            job_records, many=True)
        response = Response()

        response.data = {
            'crop_rotation_records': crop_rotation_serializer.data,
            'jobs': job_serializer.data
        }

        return response


class UpdateCropRotationView(APIView):
    def put(self, request, crop_rotation_id):
        crop_type = request.data['crop_type']
        sown_date = request.data['sown_date']
        harvest_date = request.data['harvest_date']

        try:
            cropRotationRecord = CropDataRotation.objects.get(
                crop_rotation_id=crop_rotation_id)
        except CropDataRotation.DoesNotExist:
            raise NotFound('Record not found')

        cropRotationRecord.crop_type = crop_type
        cropRotationRecord.sown_date = sown_date
        cropRotationRecord.harvest_date = harvest_date
        cropRotationRecord.save()

        cropRecords = CropDataRotation.objects.filter(
            season_id_id=cropRotationRecord.season_id)
        crop_rotation_serializer = CropRotationSerializer(
            cropRecords, many=True)
        response = Response({
            'crop_rotation_records': crop_rotation_serializer.data,
        })

        return response


class CreateFieldJobRecordsView(APIView):
    def post(self, request):

        # Extract data from the request
        farm = Farms.objects.filter(farm_id=request.data['farm_id']).first()
        if farm is None:
            raise NotFound('Farm not found!')
        season = Seasons.objects.filter(
            season_id=request.data['season_id']).first()
        if season is None:
            raise NotFound('Season not found!')

        data = {
            'job_title': request.data['job_title'],
            'farm_id': farm.farm_id,
            'season_id': season.season_id,
            'field_job_type': request.data['field_job_type'],
            'due_date': request.data['due_date'],
            'input_data': str(request.data['input_data']),
        }
        fields = request.data['fields']
        # Serialize the data
        job_serializer = JobsSerializer(data=data)

        # Validate the serializer
        if job_serializer.is_valid():
            # Save the farm record
            job_serializer.save()
            for field in fields:
                field = Fields.objects.filter(
                    field_id=field['field_id']).first()
                if field is None:
                    raise NotFound('Field not found!')
                job = Jobs.objects.filter(
                    job_id=job_serializer.data['job_id']).first()
                if job is None:
                    raise NotFound('Job not found!')

                field_data = {
                    'field_id': field.field_id,
                    'job_id': job.job_id,
                    'status': False,
                    'complete_date': "2000-01-01"
                }
                # Serialize the data
                field_job_record_serializer = FieldJobRecordsSerializer(
                    data=field_data)

                # Validate the serializer
                if field_job_record_serializer.is_valid():
                    # Save the farm record
                    field_job_record_serializer.save()
            # Respond with a success message
            jobs = Jobs.objects.filter(
                farm_id_id=farm.farm_id, season_id_id=season.season_id)
            jobs_serializer = JobsSerializer(jobs, many=True)

            response = Response({
                'jobs': jobs_serializer.data,
            })
            return response

        # If the serializer is not valid, return an error response
        return Response(job_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DisplayFieldDataView(APIView):
    def post(self, request, field_id):
        field = Fields.objects.filter(field_id=field_id).first()

        farm = Farms.objects.filter(farm_id=field.farm_id_id)
        farm_serializer = FarmsSerializer(farm, many=True)

        crop_rotation = CropDataRotation.objects.filter(
            field_id_id=field_id)
        crop_rotation_data = CropRotationSerializer(
            crop_rotation, many=True).data
        # Iterate through the crop rotation data and add season names
        for rotation in crop_rotation_data:
            season_id = rotation['season_id']
            season = Seasons.objects.filter(season_id=season_id).first()
            rotation['season_name'] = season.season_name

        print("Season ID here is: ", request.data['season_id'])
        jobs = Jobs.objects.filter(season_id_id=request.data['season_id'])
        jobs_data = JobsSerializer(jobs, many=True).data
        field_job_records = []
        for job in jobs_data:
            job_id = job['job_id']
            job_data = FieldJobRecords.objects.filter(
                job_id_id=job_id, field_id_id=field_id)
            job_data_serializer = FieldJobRecordsSerializer(
                job_data, many=True)
            if(len(job_data_serializer.data) != 0):
                job_data_serializer.data[0]['job_title'] = job['job_title']
                job_data_serializer.data[0]['due_date'] = job['due_date']

                field_job_records.append(job_data_serializer.data)
        response = Response()
        response.data = {
            'farm': farm_serializer.data[0],
            'crop_rotation_records': crop_rotation_data,
            'field_job_records': field_job_records
        }
        return response


class CreateKMLFieldView(APIView):
    def post(self, request):
        # Extract data from the request

        farm = Farms.objects.filter(farm_id=request.data['farm_id']).first()
        if farm is None:
            raise NotFound('Farm not found!')

        coordinates_list = request.data['coordinates_list']
        names_list = request.data['field_names_list']
        areas_list = request.data['areas_list']

        if len(names_list) > 1:
            for i, element in enumerate(coordinates_list):
                data = {
                    'farm_id': farm.farm_id,
                    'coordinates': str(coordinates_list[i]),
                    # The first one is always the name of the file
                    'field_name': names_list[i+1],
                    'area': areas_list[i],
                    'description': 'No description yet'
                }

                # Serialize the data
                serializer = FieldsSerializer(data=data)

                # Validate the serializer
                if serializer.is_valid():
                    # Save the farm record
                    serializer.save()
                else:
                    # If the serializer is not valid, return an error response
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            for i, element in enumerate(coordinates_list):
                data = {
                    'farm_id': farm.farm_id,
                    'coordinates': str(coordinates_list[i]),
                    'field_name': 'No name yet',  # The first one is always the name
                    'area': areas_list[i],
                    'description': 'No description yet'
                }

                # Serialize the data
                serializer = FieldsSerializer(data=data)

                # Validate the serializer
                if serializer.is_valid():
                    # Save the farm record
                    serializer.save()
                else:
                    # If the serializer is not valid, return an error response
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                    # Respond with a success message
        fields = Fields.objects.filter(farm_id_id=farm.farm_id)
        field_serializer = FieldsSerializer(fields, many=True)

        response = Response({
            'fields': field_serializer.data,
        })
        return response


class UpdateFieldJobRecordView(APIView):
    def put(self, request, job_record_id):

        try:
            fieldJobRecord = FieldJobRecords.objects.filter(
                field_job_record_id=job_record_id).first()
        except FieldJobRecords.DoesNotExist:
            raise NotFound('Record not found')

        fieldJobRecord.status = True
        fieldJobRecord.complete_date = datetime.date.today()
        fieldJobRecord.save()

        record = FieldJobRecords.objects.filter(
            field_job_record_id=fieldJobRecord.field_job_record_id).first()
        record_serializer = FieldJobRecordsSerializer(record)

        job = Jobs.objects.filter(job_id=record_serializer.data['job_id'])
        jobs_serializer = JobsSerializer(job, many=True)

        record = {
            "field_job_record_id": record_serializer.data['field_job_record_id'],
            "status": record_serializer.data['status'],
            "complete_date": record_serializer.data['complete_date'],
            "field_id": record_serializer.data['field_id'],
            "job_id": record_serializer.data['job_id'],
            "job_title": jobs_serializer.data[0]['job_title'],
            "due_date": jobs_serializer.data[0]['due_date']
        }
        response = Response({
            'field_job_record': record,

        })

        return response
