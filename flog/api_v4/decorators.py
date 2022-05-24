from apiflask import abort
from functools import wraps
from ..models import User, Post, Comment, Column, Group
from .auth.views import auth


def can_edit(permission_type: str):
    def decorator(f):
        @wraps(f)
        @auth.login_required
        def decorated_function(*args, **kwargs):
            permitted = False
            if auth.current_user is not None:
                if args[1] is not None:
                    permitted = check_permission(permission_type, args[1])
            if not permitted:
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def check_permission(permission_type: str, model_id: int) -> bool:
    permitted = False
    current_user: User = auth.current_user  # type: ignore
    if permission_type == "profile":
        permitted = auth.current_user == User.query.get_or_404(model_id)
    elif permission_type == "post":
        permitted = Post.query.get_or_404(model_id) in current_user.posts
    elif permission_type == "comment":
        permitted = Comment.query.get_or_404(model_id) in current_user.comments
    elif permission_type == "column":
        permitted = Column.query.get_or_404(model_id) in current_user.columns
    elif permission_type == "group":
        permitted = auth.current_user == Group.query.get_or_404(model_id).manager
    return permitted


def permission_required(f):
    @wraps(f)
    @auth.login_required
    def decorated_function(*args, **kwargs):
        if (auth.current_user is None) or auth.current_user.locked:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function
