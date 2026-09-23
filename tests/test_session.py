"""Session records: ID/OD circles, Z, origin. No rectangles."""

from digitizer.session import CaptureSession, CapturedCircle, sample_session


def test_empty_session() -> None:
    session = CaptureSession()
    assert session.is_empty()
    assert session.circles == []
    assert session.z_heights == []
    assert session.dxf_origin is None


def test_sample_has_id_and_od_not_rectangles() -> None:
    session = sample_session()
    kinds = {c.kind for c in session.circles}
    assert kinds == {"id", "od"}
    for circle in session.circles:
        assert circle.diameter > 0
        assert isinstance(circle.top_height, float)
    assert session.dxf_origin is not None
    assert session.z_heights
    assert not hasattr(session, "rectangles")


def test_clear_empties_file() -> None:
    session = sample_session()
    session.clear()
    assert session.is_empty()


def test_id_od_are_separate_records() -> None:
    session = CaptureSession(
        circles=[
            CapturedCircle("id", 1, 1, 1.0, 0.2),
            CapturedCircle("od", 2, 2, 2.0, 0.3),
        ]
    )
    assert [c.kind for c in session.circles] == ["id", "od"]
