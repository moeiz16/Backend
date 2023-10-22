from django.urls import path, include
# from .views import RegisterView, LoginView, UserView, LogoutView, CreateFieldView, MyView, DeleteFieldView

from .views import RegisterView, CreateFarmView, CreateSeasonView, LoginView, CreateFieldView, CreateJobView, CreateCropRotationView, CreateFieldJobRecordView, LogoutView, DisplayFieldsbyFarmView, UpdateFieldView, DeleteFieldView, DisplaySeasonCropRotationDataView, UpdateCropRotationView, CreateFieldJobRecordsView, DisplayFieldDataView, CreateKMLFieldView, UpdateFieldJobRecordView, CreateMultipleCropRotationView, DisplayJobDataView
urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    # path('user', UserView.as_view()),
    path('logout', LogoutView.as_view()),
    path('createfield', CreateFieldView.as_view()),

    path('updatefield/<int:field_id>', UpdateFieldView.as_view()),
    path('deletefield/<int:field_id>', DeleteFieldView.as_view()),
    path('createfarm', CreateFarmView.as_view()),
    path('createseason', CreateSeasonView.as_view()),
    path('createjob', CreateJobView.as_view()),
    path('createcroprotation', CreateCropRotationView.as_view()),
    path('createmultiplecroprotation', CreateMultipleCropRotationView.as_view()),
    path('createfieldjobrecord', CreateFieldJobRecordView.as_view()),
    path('displayfarmfields/<int:farm_id>', DisplayFieldsbyFarmView.as_view()),
    path('displayseasoncroprotation/<int:season_id>',
         DisplaySeasonCropRotationDataView.as_view()),
    path('updatecroprotation/<int:crop_rotation_id>',
         UpdateCropRotationView.as_view()),
    path('createfieldjobrecords', CreateFieldJobRecordsView.as_view()),
    path('displayfielddata/<int:field_id>', DisplayFieldDataView.as_view()),
    path('createkmlfields', CreateKMLFieldView.as_view()),
    path('updatefieldjobrecord/<int:job_record_id>',
         UpdateFieldJobRecordView.as_view()),
    path('displayjobdata/<int:job_id>', DisplayJobDataView.as_view()),
]
