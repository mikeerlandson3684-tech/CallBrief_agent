"""Scale mapping: envelope → canvas, Z → probe circle, features in envelope coords."""

from __future__ import annotations

import math
import unittest

from digitizer.preview.envelope import PLACEHOLDER_WORK_ENVELOPE, WorkEnvelope
from digitizer.preview.features import (
    DxfOriginMarker,
    IdCircleFeature,
    OdCircleFeature,
    ZHeightMarker,
)
from digitizer.preview.mapping import probe_circle_radius, viewport_for
from digitizer.preview.position import MachinePosition
from digitizer.preview.scene import (
    ENVELOPE_BORDER_KIND,
    GRID_KIND,
    ID_CIRCLE_KIND,
    OD_CIRCLE_KIND,
    ORIGIN_MARKER_KIND,
    PROBE_KIND,
    Z_MARKER_KIND,
    build_scene,
)

ENVELOPE = WorkEnvelope(
    x_min=0.0,
    x_max=10.0,
    y_min=0.0,
    y_max=8.0,
    z_min=0.0,
    z_max=4.0,
)
ORIGIN = MachinePosition(x=0.0, y=0.0, z=0.0)


class EnvelopeToCanvasTests(unittest.TestCase):
    def test_uniform_scale_fits_full_envelope(self) -> None:
        # 10×8 envelope in a 500×400 canvas, no padding → scale 50.
        vp = viewport_for(ENVELOPE, 500, 400, padding=0)
        self.assertAlmostEqual(vp.scale, 50.0)
        self.assertAlmostEqual(vp.drawn_width, 500.0)
        self.assertAlmostEqual(vp.drawn_height, 400.0)

    def test_letterbox_keeps_full_envelope_visible(self) -> None:
        vp = viewport_for(ENVELOPE, 400, 400, padding=0)
        self.assertAlmostEqual(vp.scale, 40.0)
        for cx, cy in vp.envelope_corners_canvas():
            self.assertGreaterEqual(cx, -1e-9)
            self.assertGreaterEqual(cy, -1e-9)
            self.assertLessEqual(cx, 400 + 1e-9)
            self.assertLessEqual(cy, 400 + 1e-9)

    def test_known_point_maps_with_y_up(self) -> None:
        vp = viewport_for(ENVELOPE, 500, 400, padding=0)
        # Machine (3, 4): x*50=150; y from top = (8-4)*50 = 200.
        cx, cy = vp.to_canvas(3.0, 4.0)
        self.assertAlmostEqual(cx, 150.0)
        self.assertAlmostEqual(cy, 200.0)

    def test_y_max_is_near_canvas_top(self) -> None:
        vp = viewport_for(ENVELOPE, 500, 400, padding=0)
        _, y_max_cy = vp.to_canvas(0.0, ENVELOPE.y_max)
        _, y_min_cy = vp.to_canvas(0.0, ENVELOPE.y_min)
        self.assertLess(y_max_cy, y_min_cy)

    def test_placeholder_envelope_is_flagged(self) -> None:
        self.assertTrue(PLACEHOLDER_WORK_ENVELOPE.is_placeholder)
        self.assertEqual(PLACEHOLDER_WORK_ENVELOPE.source, "placeholder-not-measured")

    def test_rejects_inverted_limits(self) -> None:
        with self.assertRaises(ValueError):
            WorkEnvelope(0, 0, 0, 1, 0, 1)


class ZoomToPartRejectedTests(unittest.TestCase):
    def test_scale_does_not_depend_on_feature_extent(self) -> None:
        pos = MachinePosition(5.0, 4.0, 1.0)
        empty = build_scene(
            ENVELOPE,
            pos,
            (),
            canvas_width=500,
            canvas_height=400,
            grid_step=1.0,
            padding=0,
        )
        tiny = build_scene(
            ENVELOPE,
            pos,
            (IdCircleFeature(1.0, 1.0, diameter=0.2),),
            canvas_width=500,
            canvas_height=400,
            grid_step=1.0,
            padding=0,
        )
        huge = build_scene(
            ENVELOPE,
            pos,
            (OdCircleFeature(5.0, 4.0, diameter=40.0),),
            canvas_width=500,
            canvas_height=400,
            grid_step=1.0,
            padding=0,
        )
        self.assertAlmostEqual(empty.scale, tiny.scale)
        self.assertAlmostEqual(empty.scale, huge.scale)
        self.assertAlmostEqual(empty.scale, 50.0)


class ZToCircleSizeTests(unittest.TestCase):
    def test_z_min_is_smallest_circle(self) -> None:
        small = probe_circle_radius(0.0, ENVELOPE, min_radius=10.0, max_radius=30.0)
        large = probe_circle_radius(4.0, ENVELOPE, min_radius=10.0, max_radius=30.0)
        self.assertAlmostEqual(small, 10.0)
        self.assertAlmostEqual(large, 30.0)
        self.assertGreater(large, small)

    def test_linear_between_min_and_max(self) -> None:
        mid = probe_circle_radius(2.0, ENVELOPE, min_radius=10.0, max_radius=30.0)
        self.assertAlmostEqual(mid, 20.0)

    def test_clamps_outside_envelope_z(self) -> None:
        below = probe_circle_radius(-8.0, ENVELOPE, min_radius=10.0, max_radius=30.0)
        above = probe_circle_radius(99.0, ENVELOPE, min_radius=10.0, max_radius=30.0)
        self.assertAlmostEqual(below, 10.0)
        self.assertAlmostEqual(above, 30.0)

    def test_scene_probe_grows_with_z(self) -> None:
        kwargs = dict(
            envelope=ENVELOPE,
            features=(),
            canvas_width=500,
            canvas_height=400,
            grid_step=1.0,
            padding=0,
            probe_min_radius=10.0,
            probe_max_radius=30.0,
        )
        low = build_scene(position=MachinePosition(1, 1, 0), **kwargs)
        high = build_scene(position=MachinePosition(1, 1, 4), **kwargs)
        r_low = low.circles_of(PROBE_KIND)[0].radius
        r_high = high.circles_of(PROBE_KIND)[0].radius
        self.assertAlmostEqual(r_low, 10.0)
        self.assertAlmostEqual(r_high, 30.0)


class CapturedFeaturesTests(unittest.TestCase):
    def test_id_circle_center_and_diameter_in_envelope_coords(self) -> None:
        feature = IdCircleFeature(center_x=3.0, center_y=4.0, diameter=2.0)
        scene = build_scene(
            ENVELOPE,
            ORIGIN,
            (feature,),
            canvas_width=500,
            canvas_height=400,
            grid_step=1.0,
            padding=0,
            probe_min_radius=5.0,
            probe_max_radius=5.0,
        )
        drawn = scene.circles_of(ID_CIRCLE_KIND)
        self.assertEqual(len(drawn), 1)
        self.assertAlmostEqual(drawn[0].cx, 150.0)
        self.assertAlmostEqual(drawn[0].cy, 200.0)
        self.assertAlmostEqual(drawn[0].radius, 50.0)  # radius 1.0 × scale 50
        self.assertAlmostEqual(drawn[0].machine_diameter, 2.0)

    def test_od_circle_drawn_in_envelope_coords(self) -> None:
        feature = OdCircleFeature(center_x=7.0, center_y=2.0, diameter=1.0)
        scene = build_scene(
            ENVELOPE,
            ORIGIN,
            (feature,),
            canvas_width=500,
            canvas_height=400,
            grid_step=1.0,
            padding=0,
        )
        drawn = scene.circles_of(OD_CIRCLE_KIND)
        self.assertEqual(len(drawn), 1)
        self.assertAlmostEqual(drawn[0].cx, 350.0)
        self.assertAlmostEqual(drawn[0].cy, 300.0)
        self.assertAlmostEqual(drawn[0].radius, 25.0)

    def test_z_and_origin_markers_use_envelope_xy(self) -> None:
        scene = build_scene(
            ENVELOPE,
            ORIGIN,
            (
                ZHeightMarker(x=3.0, y=4.0, z=1.25),
                DxfOriginMarker(x=1.0, y=1.0),
            ),
            canvas_width=500,
            canvas_height=400,
            grid_step=1.0,
            padding=0,
        )
        z_mark = scene.markers_of(Z_MARKER_KIND)
        origin = scene.markers_of(ORIGIN_MARKER_KIND)
        self.assertEqual(len(z_mark), 1)
        self.assertEqual(len(origin), 1)
        self.assertAlmostEqual(z_mark[0].cx, 150.0)
        self.assertAlmostEqual(z_mark[0].cy, 200.0)
        self.assertAlmostEqual(origin[0].cx, 50.0)
        self.assertAlmostEqual(origin[0].cy, 350.0)

    def test_empty_file_is_envelope_grid_and_probe_only(self) -> None:
        scene = build_scene(
            ENVELOPE,
            MachinePosition(2.0, 3.0, 1.0),
            (),
            canvas_width=500,
            canvas_height=400,
            grid_step=1.0,
            padding=0,
        )
        self.assertTrue(scene.lines_of(GRID_KIND))
        self.assertEqual(len(scene.lines_of(ENVELOPE_BORDER_KIND)), 4)
        self.assertEqual(len(scene.circles_of(PROBE_KIND)), 1)
        self.assertEqual(scene.circles_of(ID_CIRCLE_KIND), ())
        self.assertEqual(scene.circles_of(OD_CIRCLE_KIND), ())
        self.assertEqual(scene.markers, ())
        probe = scene.circles_of(PROBE_KIND)[0]
        self.assertAlmostEqual(probe.cx, 100.0)
        self.assertAlmostEqual(probe.cy, 250.0)

    def test_grid_includes_envelope_edges(self) -> None:
        scene = build_scene(
            ENVELOPE,
            ORIGIN,
            (),
            canvas_width=500,
            canvas_height=400,
            grid_step=1.0,
            padding=0,
        )
        vertical = [
            line.x1
            for line in scene.lines_of(GRID_KIND)
            if math.isclose(line.x1, line.x2)
        ]
        self.assertAlmostEqual(min(vertical), 0.0)
        self.assertAlmostEqual(max(vertical), 500.0)

    def test_all_session_features_are_drawn_together(self) -> None:
        features = (
            IdCircleFeature(3.0, 5.0, 1.6),
            OdCircleFeature(7.0, 2.5, 1.2),
            ZHeightMarker(3.0, 5.0, 1.2),
            DxfOriginMarker(1.0, 1.0),
        )
        scene = build_scene(
            ENVELOPE,
            ORIGIN,
            features,
            canvas_width=500,
            canvas_height=400,
            grid_step=1.0,
            padding=0,
        )
        self.assertEqual(len(scene.circles_of(ID_CIRCLE_KIND)), 1)
        self.assertEqual(len(scene.circles_of(OD_CIRCLE_KIND)), 1)
        self.assertEqual(len(scene.markers_of(Z_MARKER_KIND)), 1)
        self.assertEqual(len(scene.markers_of(ORIGIN_MARKER_KIND)), 1)
        self.assertEqual(len(scene.circles_of(PROBE_KIND)), 1)


if __name__ == "__main__":
    unittest.main()
