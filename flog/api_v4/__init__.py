from apiflask import APIBlueprint
from .authentication import auth_bp
from .me import me_bp

api_v4_bp = APIBlueprint("api_v4", __name__, url_prefix="/v4/")

@api_v4_bp.get("/")
def index():
    """
    help API of version 4.x
    """
    return {
        "/auth/": "authentication",
        "/me/": "current user"
    }