import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest
import tkinter as tk
from aceest_app import ACEestApp

@pytest.fixture
def app():
    """Fixture to create and destroy the Tkinter app safely in headless CI."""
    root = tk.Tk()
    root.withdraw()
    app = ACEestApp(root)
    yield app
    root.destroy()

def test_programs_exist(app):
    """Ensure all expected programs are defined."""
    assert "Fat Loss (FL)" in app.programs
    assert "Muscle Gain (MG)" in app.programs
    assert "Beginner (BG)" in app.programs

def test_update_display_fat_loss(app):
    """Check that selecting Fat Loss updates labels correctly."""
    app.prog_var.set("Fat Loss (FL)")
    app.update_display(None)

    data = app.programs["Fat Loss (FL)"]
    assert app.work_label.cget("text") == data["workout"]
    assert app.work_label.cget("fg") == data["color"]
    assert app.diet_label.cget("text") == data["diet"]

def test_update_display_muscle_gain(app):
    """Check that selecting Muscle Gain updates labels correctly."""
    app.prog_var.set("Muscle Gain (MG)")
    app.update_display(None)

    data = app.programs["Muscle Gain (MG)"]
    assert app.work_label.cget("text") == data["workout"]
    assert app.work_label.cget("fg") == data["color"]
    assert app.diet_label.cget("text") == data["diet"]

def test_update_display_beginner(app):
    """Check that selecting Beginner updates labels correctly."""
    app.prog_var.set("Beginner (BG)")
    app.update_display(None)

    data = app.programs["Beginner (BG)"]
    assert app.work_label.cget("text") == data["workout"]
    assert app.work_label.cget("fg") == data["color"]
    assert app.diet_label.cget("text") == data["diet"]
