from apiflask import APIBlueprint
from flask.views import MethodView

from ...models import User
from ..decorators import can_edit
from .schemas import PublicUserOutSchema

user_bp = APIBlueprint("user", __name__)


@user_bp.route("/user/<int:user_id>", endpoint="user")
class UserAPI(MethodView):
    @user_bp.output(PublicUserOutSchema)
    def get(self, user_id: int):
        """Return the public information of a certain user"""
        return User.query.get_or_404(user_id)

    @can_edit("profile")
    @user_bp.output(PublicUserOutSchema)
    def patch(self, user_id: int):
        """Lock or unlock a user"""
        user = User.query.get_or_404(user_id)
        user.locked = not user.locked
        return user
