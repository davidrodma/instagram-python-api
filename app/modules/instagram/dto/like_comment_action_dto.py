from pydantic import BaseModel

class LikeCommentActionDto(BaseModel):
    username_action: str
    comment_id: str = ""
    username_comment: str = ""
    url_target: str = ""
    id_target: str = ""
    user_id_comment: str = ""
    max: int = 100,