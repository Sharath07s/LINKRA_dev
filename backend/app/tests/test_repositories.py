from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    pass


def test_repo_create(db):
    repo = UserRepository(User)
    user_data = {"badge_number": "R123", "email": "repo@ksp.gov.in"}
    user = repo.create(db, obj_in=user_data)
    
    assert user.id is not None
    assert user.badge_number == "R123"


def test_repo_soft_delete(db):
    repo = UserRepository(User)
    user = repo.create(db, obj_in={"badge_number": "D123", "email": "del2@ksp.gov.in"})
    
    repo.delete(db, id=user.id)
    
    # get should not return soft-deleted
    fetched = repo.get(db, id=user.id)
    assert fetched is None
    
    # but it is in db
    raw = db.query(User).get(user.id)
    assert raw is not None
    assert raw.is_deleted is True
