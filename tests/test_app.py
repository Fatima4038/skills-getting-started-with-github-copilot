from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_get_activities_returns_known_activity():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_adds_new_participant():
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Ensure cleanup in case the email already exists
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]

    # Cleanup after test
    activities[activity_name]["participants"].remove(email)


def test_duplicate_signup_returns_bad_request():
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"

    activities[activity_name]["participants"].append(email)
    try:
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
        assert activities[activity_name]["participants"].count(email) == 1
    finally:
        activities[activity_name]["participants"].remove(email)


def test_remove_participant_from_activity():
    activity_name = "Programming Class"
    email = "remove-me@mergington.edu"

    activities[activity_name]["participants"].append(email)
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_delete_nonexistent_participant_returns_not_found():
    activity_name = "Programming Class"
    email = "missing@mergington.edu"

    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found in activity"


def test_delete_from_nonexistent_activity_returns_not_found():
    response = client.delete("/activities/NotAnActivity/participants?email=test@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
