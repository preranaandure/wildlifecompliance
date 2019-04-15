import traceback
import base64
import geojson
from django.db.models import Q, Min
from django.db import transaction
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.conf import settings
from wildlifecompliance import settings
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework import viewsets, serializers, status, generics, views
import rest_framework.exceptions as rest_exceptions
from rest_framework.decorators import (
        detail_route, 
        list_route, 
        renderer_classes, 
        parser_classes,
        api_view
        )
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, BasePermission
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta
from collections import OrderedDict
from django.core.cache import cache
from ledger.accounts.models import EmailUser, Address
from ledger.address.models import Country
from ledger.checkout.utils import calculate_excl_gst
from datetime import datetime, timedelta, date
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from wildlifecompliance.helpers import is_customer, is_internal
from wildlifecompliance.components.call_email.models import CallEmail, Classification
from wildlifecompliance.components.call_email.serializers import (
        CallEmailSerializer, 
        ClassificationSerializer, 
        CreateCallEmailSerializer,
        UpdateRendererDataSerializer,
        )
from wildlifecompliance.components.applications.utils import (                                                                                                                                              
            SchemaParser,                                                                                                                                                            
            MissingFieldsException
            )

class CallEmailViewSet(viewsets.ModelViewSet):
    queryset = CallEmail.objects.all()
    serializer_class = CallEmailSerializer
    
    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return CallEmail.objects.all()
        return CallEmail.objects.none()

    @list_route(methods=['GET', ])
    def datatable_list(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset()
            serializer = self.get_serializer(
                qs, many=True, context={'request': request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def create(self, request, *args, **kwargs):
        print("create")
        print(request.data)
        try:
            request_classification_str = request.data.get(
                        'classification')
            request_classification_obj = Classification.objects.get(
                    name=request_classification_str.capitalize())
            parser = SchemaParser()
            form_data = request.data.get('schema')
            parsed_json = parser.create_data_from_form(form_data)
            request_data = {
                    'status': request.data.get('status'),
                    'classification': request_classification_obj.id, 
                    'number': request.data.get('number'),
                    'caller': request.data.get('caller'),
                    'assigned_to': request.data.get('assigned_to'),
                    'data': parsed_json,
                    }
            serializer = CreateCallEmailSerializer(data=request_data)
            serializer.is_valid(raise_exception=True)
            if serializer.is_valid():
                serializer.save()
                headers = self.get_success_headers(serializer.data)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                    headers=headers
                    )
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))
    
    @detail_route(methods=['POST', ])
    @renderer_classes((JSONRenderer,))
    def update_renderer_form(self, request, *args, **kwargs):
        print("update")
        print(request.POST)
        
        try:
            parser = SchemaParser()
            # form_data = request.data.get('schema')
            instance = self.get_object()
            #print(instance)
            parsed_json = parser.create_data_from_form(
                    instance.report_type.schema, 
                    request.POST, 
                    #instance.report_type.schema,
                    #file_data=False,
                    request.FILES,
                    comment_data=True
                    )
            rendered_data = parsed_json[0]
            instance.data = rendered_data
            data = {
                    'data': rendered_data,
                    }
            serializer = UpdateRendererDataSerializer(instance, data=data)
            serializer.is_valid(raise_exception=True)
            if serializer.is_valid():
                serializer.save()
                headers = self.get_success_headers(serializer.data)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                    headers=headers
                    )
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

