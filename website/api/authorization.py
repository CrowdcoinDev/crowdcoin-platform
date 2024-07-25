from tastypie.exceptions import Unauthorized
from tastypie.authorization import *
import logging
from website.models import *
logger = logging.getLogger(__name__)

class UserAuthorization(ReadOnlyAuthorization):
    '''
    Default Authentication class for ``Resource`` objects.

    Only allows ``GET`` requests.
    '''
    def read_list(self, object_list, bundle):
        return object_list.filter(user=bundle.request.user)

    def read_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user

    def create_list(self, object_list, bundle):
        return []

    def create_detail(self, object_list, bundle):
        raise Unauthorized('You are not allowed to access that resource.')

    def update_list(self, object_list, bundle):
        return object_list.filter(user=bundle.request.user)

    def update_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user

    def delete_list(self, object_list, bundle):
        return []

    def delete_detail(self, object_list, bundle):
        raise Unauthorized('You are not allowed to access that resource.')

class ProfileAuthorization(ReadOnlyAuthorization):
    '''
    Default Authentication class for ``Resource`` objects.

    Only allows ``GET`` requests.
    '''
    def read_list(self, object_list, bundle):
        return object_list.filter(profile__user=bundle.request.user)

    def read_detail(self, object_list, bundle):
        return bundle.obj.profile.user == bundle.request.user

    def create_list(self, object_list, bundle):
        return object_list.filter(profile__user=bundle.request.user)

    def create_detail(self, object_list, bundle):
        return bundle.obj.profile.user == bundle.request.user

    def update_list(self, object_list, bundle):
        return object_list.filter(profile__user=bundle.request.user)

    def update_detail(self, object_list, bundle):
        return bundle.obj.profile.user == bundle.request.user

    def delete_list(self, object_list, bundle):
        return []

    def delete_detail(self, object_list, bundle):
        raise Unauthorized('You are not allowed to access that resource.')

class PocketAuthorization(ReadOnlyAuthorization):
    '''
    Default Authentication class for ``Resource`` objects.

    Only allows ``GET`` requests.
    '''
    def read_list(self, object_list, bundle):
        user_profile = UserProfile.objects.get(user=bundle.request.user)
        if bundle.request.user.is_superuser :
            return object_list
        return object_list.filter(pocket__in=user_profile.pockets.all())

    def read_detail(self, object_list, bundle):
        user_profile = UserProfile.objects.get(user=bundle.request.user)
        if bundle.request.user.is_superuser or bundle.obj.pocket in user_profile.pockets.all():
            return True
        return False

    def create_list(self, object_list, bundle):
        user_profile = UserProfile.objects.get(user=bundle.request.user)
        return bundle #.filter(pocket__in=user_profile.pockets.all())

    def create_detail(self, object_list, bundle):
        user_profile = UserProfile.objects.get(user=bundle.request.user)
        # import pdb; pdb.set_trace()
        if bundle.request.user.is_superuser or bundle.obj.pocket in user_profile.pockets.all():
            return True
        return False

    def update_list(self, object_list, bundle):
        user_profile = UserProfile.objects.get(user=bundle.request.user)
        if bundle.request.user.is_superuser :
            return object_list
        return object_list.filter(pocket__in=user_profile.pockets.all())

    def update_detail(self, object_list, bundle):
        user_profile = UserProfile.objects.get(user=bundle.request.user)

        if bundle.request.user.is_superuser or bundle.obj.pocket in user_profile.pockets.all():
            return True
        return False

    def delete_list(self, object_list, bundle):
        return []

    def delete_detail(self, object_list, bundle):
        raise Unauthorized('You are not allowed to access that resource.')

