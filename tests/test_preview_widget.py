"""Tkinter PreviewCanvas smoke tests (display or xvfb)."""

from __future__ import annotations

import unittest

try:
    import tkinter as tk
except ImportError:  # pragma: no cover
    tk = None  # type: ignore[assignment]

from digitizer.preview.envelope import PLACEHOLDER_WORK_ENVELOPE
from digitizer.preview.features import IdCircleFeature
from digitizer.preview.position import MachinePosition
from digitizer.preview.scene import ID_CIRCLE_KIND, PROBE_KIND
from digitizer.preview.widget import PreviewCanvas


def _tk_root() -> tk.Tk | None:
    if tk is None:
        return None
    try:
        root = tk.Tk()
    except tk.TclError:
        return None
    root.withdraw()
    return root


class PreviewCanvasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = _tk_root()

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.root is not None:
            cls.root.destroy()

    def setUp(self) -> None:
        if self.root is None:
            self.skipTest("Tkinter display not available")

    def test_refresh_paints_probe_and_id_circle(self) -> None:
        widget = PreviewCanvas(
            self.root,
            envelope=PLACEHOLDER_WORK_ENVELOPE,
            position=MachinePosition(2.0, 3.0, 1.0),
            features=(IdCircleFeature(3.0, 4.0, 1.0),),
            width=400,
            height=320,
        )
        widget.update_idletasks()
        widget.canvas.config(width=400, height=320)
        widget.update()
        widget.refresh()
        self.assertIsNotNone(widget.scene)
        assert widget.scene is not None
        self.assertEqual(len(widget.scene.circles_of(PROBE_KIND)), 1)
        self.assertEqual(len(widget.scene.circles_of(ID_CIRCLE_KIND)), 1)
        self.assertTrue(widget.canvas.find_withtag("probe"))
        self.assertTrue(widget.canvas.find_withtag("id_circle"))
        self.assertTrue(widget.canvas.find_withtag("grid"))
        widget.destroy()

    def test_empty_file_has_no_feature_tags(self) -> None:
        widget = PreviewCanvas(
            self.root,
            envelope=PLACEHOLDER_WORK_ENVELOPE,
            position=MachinePosition(1.0, 1.0, 0.0),
            features=(),
            width=400,
            height=320,
        )
        widget.update()
        widget.refresh()
        self.assertFalse(widget.canvas.find_withtag("id_circle"))
        self.assertFalse(widget.canvas.find_withtag("od_circle"))
        self.assertFalse(widget.canvas.find_withtag("z_marker"))
        self.assertFalse(widget.canvas.find_withtag("dxf_origin"))
        self.assertTrue(widget.canvas.find_withtag("probe"))
        self.assertTrue(widget.canvas.find_withtag("grid"))
        self.assertIn("PLACEHOLDER", widget._caption.cget("text"))
        widget.destroy()


if __name__ == "__main__":
    unittest.main()
