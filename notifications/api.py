from tastypie.authorization import Authorization

__author__ = 'danielqiu'
from tastypie.resources import ModelResource
from models import Notification
from tastypie.serializers import Serializer


class AllNotificationAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(recipient=bundle.request.user)

    def read_detail(self, object_list, bundle):
        return object_list.filter(recipient=bundle.request.user)


class AllNotificationResource(ModelResource):

    class Meta:
        queryset = Notification.objects.all()
        resource_name = 'all_notification'
        serializer = Serializer()
        authorization = AllNotificationAuthorization()
        excludes = ['public', 'level']

    def dehydrate(self, bundle):
        bundle.data['data'] = bundle.obj.data
        return bundle


class UnreadNotificationAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(recipient=bundle.request.user, unread=True)

    def read_detail(self, object_list, bundle):
        return object_list.filter(recipient=bundle.request.user, unread=True)


class UnreadNotificationResource(ModelResource):

    class Meta:
        queryset = Notification.objects.all()
        resource_name = 'unread_notification'
        serializer = Serializer()
        authorization = UnreadNotificationAuthorization()


