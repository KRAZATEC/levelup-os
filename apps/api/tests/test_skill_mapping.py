from app.schemas import QuestCreate

def test_skill_slugs_are_limited():
    payload = QuestCreate(title="Build API", skill_slugs=["backend-engineering", "cloud-devops"])
    assert payload.skill_slugs == ["backend-engineering", "cloud-devops"]

def test_skill_slugs_default_empty():
    payload = QuestCreate(title="Read documentation")
    assert payload.skill_slugs == []
