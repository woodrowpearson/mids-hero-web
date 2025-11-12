from app.models import Power


def test_power_has_source_metadata_field():
    """Test that Power model has source_metadata JSON field"""
    assert hasattr(Power, "source_metadata")


def test_power_has_tags_array_field():
    """Test that Power model has tags array field"""
    assert hasattr(Power, "tags")


def test_power_has_requires_array_field():
    """Test that Power model has requires array field"""
    assert hasattr(Power, "requires")
