from app.models.user import User


def test_create_user(db):
    user = User(badge_number="12345", email="test@ksp.gov.in", first_name="Test", last_name="User")
    db.add(user)
    db.commit()
    
    assert user.id is not None
    assert user.badge_number == "12345"
    assert user.is_deleted is False
    assert user.created_at is not None


def test_soft_delete(db):
    user = User(badge_number="999", email="del@ksp.gov.in")
    db.add(user)
    db.commit()
    
    # Soft delete manually
    user.is_deleted = True
    db.commit()
    
    fetched = db.query(User).filter_by(badge_number="999").first()
    assert fetched.is_deleted is True
