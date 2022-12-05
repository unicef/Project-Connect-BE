from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param

from proco.utils.cache import cache_manager


class UseCachedDataMixin(object):
    CACHE_KEY = 'cache'

    def use_cached_data(self):
        return self.request.query_params.get(self.CACHE_KEY, 'on').lower() in ['on', 'true']


class CachedListMixin(UseCachedDataMixin):
    LIST_CACHE_KEY_PREFIX = None

    def get_list_cache_key(self):
        params = dict(self.request.query_params)
        params.pop(self.CACHE_KEY, None)
        return '{0}_{1}'.format(
            getattr(self.__class__, 'LIST_CACHE_KEY_PREFIX', self.__class__.__name__) or self.__class__.__name__,
            '_'.join(map(lambda x: '{0}_{1}'.format(x[0], x[1]), sorted(params.items()))),
        )

    def _get_raw_list_response(self, request, *args, **kwargs):
        cache_key = self.get_list_cache_key()
        response = super(CachedListMixin, self).list(request, *args, **kwargs)
        request_path = remove_query_param(request.get_full_path(), self.CACHE_KEY)
        cache_manager.set(cache_key, response.data, request_path=request_path)
        return response

    def list(self, request, *args, **kwargs):
        if not self.use_cached_data():
            return self._get_raw_list_response(request, *args, **kwargs)
        else:
            cache_key = self.get_list_cache_key()
            data = cache_manager.get(cache_key)
            if not data:
                return self._get_raw_list_response(request, *args, **kwargs)
            return Response(data=data)


class CachedRetrieveMixin(UseCachedDataMixin):
    RETRIEVE_CACHE_KEY_PREFIX = None

    def get_retrieve_cache_key(self):
        return '{0}_{1}'.format(
            getattr(self.__class__, 'RETRIEVE_CACHE_KEY_PREFIX', self.__class__.__name__) or self.__class__.__name__,
            '_'.join(map(lambda x: '{0}_{1}'.format(x[0], x[1]), sorted(self.kwargs.items()))),
        )

    def _get_raw_retrieve_response(self, request, *args, **kwargs):
        cache_key = self.get_retrieve_cache_key()
        response = super(CachedRetrieveMixin, self).retrieve(request, *args, **kwargs)
        request_path = remove_query_param(request.get_full_path(), self.CACHE_KEY)
        cache_manager.set(cache_key, response.data, request_path=request_path)
        return response

    def retrieve(self, request, *args, **kwargs):
        if not self.use_cached_data():
            return self._get_raw_retrieve_response(request, *args, **kwargs)
        else:
            cache_key = self.get_retrieve_cache_key()
            data = cache_manager.get(cache_key)
            if not data:
                return self._get_raw_retrieve_response(request, *args, **kwargs)
            return Response(data=data)
