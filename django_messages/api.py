from django_messages.models import Message
from tastypie.authorization import Authorization
from tastypie.serializers import Serializer
from traveller.api import UserResource, TravellerResource

__author__ = 'danielqiu'

from tastypie.resources import ModelResource
from tastypie import fields

from tastypie.paginator import Paginator

class SentMessageAuthorization(Authorization):

    def read_list(self, object_list, bundle):
        return object_list.filter(sender=bundle.request.user, sender_deleted_at=None)
    def read_detail(self, object_list, bundle):
        if bundle.obj.sender == bundle.request.user:
            return True
        else:
            return False


class SentMessageResource(ModelResource):

    messageSubject = fields.CharField(attribute='subject')
    messageBody = fields.CharField(attribute='body')

    class Meta:
        queryset = Message.objects.all()
        resource_name = 'sent_message'
        authorization = SentMessageAuthorization()
        fields=['messageSubject', 'messageBody']

    def dehydrate(self, bundle):
        bundle.data['senderName'] = bundle.obj.sender.username
        bundle.data['recipientName'] = bundle.obj.recipient.username
        bundle.data['senderURL'] = bundle.obj.sender.profile.get_absolute_url()
        bundle.data['recipientURL'] = bundle.obj.recipient.profile.get_absolute_url()
        bundle.data['userAvatarImg'] = 'accounts/profile/' + bundle.obj.recipient.profile.get_avatar_url(50)
        bundle.data['messageURL'] = bundle.obj.get_absolute_url()
        bundle.data['messageID'] = bundle.obj.id
        return bundle



class ReceivedMessageAuthorization(Authorization):

    def read_list(self, object_list, bundle):
        return object_list.filter(recipient=bundle.request.user, recipient_deleted_at=None)
    def read_detail(self, object_list, bundle):
        return bundle.obj.recipient == bundle.request.user

class ReceivedMessageResource(ModelResource):

    messageSubject = fields.CharField(attribute='subject')
    messageBody = fields.CharField(attribute='body')

    class Meta:
        queryset = Message.objects.all()
        resource_name = 'received_message'
        authorization = ReceivedMessageAuthorization()
        fields = ['messageSubject', 'messageBody']

    def dehydrate(self, bundle):
        bundle.data['senderName'] = bundle.obj.sender.username
        bundle.data['recipientName'] = bundle.obj.recipient.username
        bundle.data['senderURL'] = bundle.obj.sender.profile.get_absolute_url()
        bundle.data['recipientURL'] = bundle.obj.recipient.profile.get_absolute_url()
        bundle.data['userAvatarImg'] = 'accounts/profile/' + bundle.obj.sender.profile.get_avatar_url(50)
        bundle.data['messageURL'] = bundle.obj.get_absolute_url()
        bundle.data['messageID'] = bundle.obj.id

        if bundle.obj.new():
            bundle.data['isUnread'] = True
        else:
            bundle.data['isUnread'] = False
        return bundle


class TrashMessageAuthorization(Authorization):


    def read_list(self, object_list, bundle):
        return object_list.filter(
            recipient=bundle.request.user,
            recipient_deleted_at__isnull=False,
        ) | object_list.filter(
            sender=bundle.request.user,
            sender_deleted_at__isnull=False,
        )

    def read_detail(self, object_list, bundle):

        return bundle.obj.sender == bundle.request.user or bundle.obj.recipient == bundle.request.user

class TrashMessageResource(ModelResource):
    messageSubject = fields.CharField(attribute='subject')
    messageBody = fields.CharField(attribute='body')

    class Meta:
        queryset = Message.objects.all()
        resource_name = 'deleted_message'
        authorization = TrashMessageAuthorization()
        fields = ['messageSubject', 'messageBody']

    def dehydrate(self, bundle):
        bundle.data['senderName'] = bundle.obj.sender.username
        bundle.data['recipientName'] = bundle.obj.recipient.username
        bundle.data['senderURL'] = bundle.obj.sender.profile.get_absolute_url()
        bundle.data['recipientURL'] = bundle.obj.recipient.profile.get_absolute_url()
        bundle.data['messageURL'] = bundle.obj.get_absolute_url()
        bundle.data['messageID'] = bundle.obj.id

        if bundle.obj.sender == bundle.request.user:
            bundle.data['userAvatarImg'] = 'accounts/profile/'+bundle.obj.recipient.profile.get_avatar_url(50)
            bundle.data['isFromMe'] = True
        else:
            bundle.data['userAvatarImg'] = 'accounts/profile/'+bundle.obj.sender.profile.get_avatar_url(50)
            bundle.data['isFromMe'] = False
            if bundle.obj.new():
                bundle.data['isUnread'] = True
            else:
                bundle.data['isUnread'] = False
        return bundle

    def alter_list_data_to_serialize(self, request, data):
        data['meta']['currentUser'] = request.user
        return data