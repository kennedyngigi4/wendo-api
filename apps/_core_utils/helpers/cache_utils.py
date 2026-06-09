from django.core.cache import cache

class GlobalCache:

    DEFAULT_TIMEOUT = 60 * 10

    # ===============================================================
    #  PUBLIC CACHES
    # ===============================================================
    @staticmethod
    def get_list_public_key(prefix):
        return f"{prefix}"
    
    @staticmethod
    def get_detail_public_key(prefix, item_id):
        return f"{prefix}_{item_id}"
    


    # ===============================================================
    #  PRIVATE CACHES
    # ===============================================================
    @staticmethod
    def get_list_cache_key(prefix, user_id):
        return f"{prefix}_{user_id}"
    

    @staticmethod
    def get_detail_cache_key(prefix, user_id, item_id):
        return f"{prefix}_{user_id}_{item_id}"
    

    @staticmethod
    def clear_cache(prefix, user_id, item_id=None):
        cache.delete(
            GlobalCache().get_list_cache_key(prefix, user_id)
        )


        if item_id:
            cache.delete(
                GlobalCache().get_detail_cache_key(
                    prefix, 
                    user_id, 
                    item_id
                )
            )


        