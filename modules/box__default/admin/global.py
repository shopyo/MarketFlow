from flask_login import current_user


def user_is_marketplace_owner():
    if hasattr(current_user, 'is_authenticated'):
        if current_user.is_authenticated:
            if hasattr(current_user, 'is_admin'):
                if current_user.is_admin:
                    return True

    return False

available_everywhere = {
    'user_is_marketplace_owner': user_is_marketplace_owner
}