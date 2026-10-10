import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest
import tkinter as tk
from tkinter import messagebox
from aceest_app import ACEestApp

@pytest.fixture
def app(monkeypatch):
    """Fixture to create and destroy the Tkinter app safely in headless CI."""
    root = tk.Tk()
    root.withdraw()  # Prevents GUI window from showing
    app = ACEestApp(root)
    yield app
    root.destroy()

def test_programs_exist(app):
    """Ensure all expected programs are defined."""
    assert "Fat Loss (FL)" in app.programs
    assert "Muscle Gain (MG)" in app.programs
    assert "Beginner (BG)" in app.programs

def test_update_program_fat_loss(app):
    """Check that selecting Fat Loss updates workout, diet, and calories."""
    app.weight_var.set(70)  # simulate client weight
    app.program_var.set("Fat Loss (FL)")
    app.update_program()

    data = app.programs["Fat Loss (FL)"]
    assert data["workout"] in app.workout_text.get("1.0", "end")
    assert data["diet"] in app.diet_text.get("1.0", "end")
    expected_calories = int(70 * data["calorie_factor"])
    assert f"{expected_calories} kcal" in app.calorie_label.cget("text")

def test_update_program_muscle_gain(app):
    """Check that selecting Muscle Gain updates workout, diet, and calories."""
    app.weight_var.set(80)
    app.program_var.set("Muscle Gain (MG)")
    app.update_program()

    data = app.programs["Muscle Gain (MG)"]
    assert data["workout"] in app.workout_text.get("1.0", "end")
    assert data["diet"] in app.diet_text.get("1.0", "end")
    expected_calories = int(80 * data["calorie_factor"])
    assert f"{expected_calories} kcal" in app.calorie_label.cget("text")

def test_update_program_beginner(app):
    """Check that selecting Beginner updates workout, diet, and calories."""
    app.weight_var.set(60)
    app.program_var.set("Beginner (BG)")
    app.update_program()

    data = app.programs["Beginner (BG)"]
    assert data["workout"] in app.workout_text.get("1.0", "end")
    assert data["diet"] in app.diet_text.get("1.0", "end")
    expected_calories = int(60 * data["calorie_factor"])
    assert f"{expected_calories} kcal" in app.calorie_label.cget("text")

def test_reset_clears_fields(app):
    """Ensure reset clears all fields and labels."""
    app.name_var.set("Test User")
    app.age_var.set(25)
    app.weight_var.set(70)
    app.program_var.set("Fat Loss (FL)")
    app.progress_var.set(80)
    app.update_program()

    app.reset()

    assert app.name_var.get() == ""
    assert app.age_var.get() == 0
    assert app.weight_var.get() == 0
    assert app.program_var.get() == ""
    assert app.progress_var.get() == 0
    assert app.workout_text.get("1.0", "end").strip() == ""
    assert app.diet_text.get("1.0", "end").strip() == ""
    assert app.calorie_label.cget("text") == "Estimated Calories: --"

def test_save_client_incomplete(monkeypatch, app):
    """Ensure save_client warns when name or program missing."""
    called = {}

    def fake_warning(title, message):
        called["warning"] = (title, message)

    monkeypatch.setattr(messagebox, "showwarning", fake_warning)

    app.name_var.set("")
    app.program_var.set("")
    app.save_client()

    assert "warning" in called
    assert "Incomplete" in called["warning"][0]

def test_save_client_success(monkeypatch, app):
    """Ensure save_client shows info when valid data provided."""
    called = {}

    def fake_info(title, message):
        called["info"] = (title, message)

    monkeypatch.setattr(messagebox, "showinfo", fake_info)

    app.name_var.set("Senthil")
    app.program_var.set("Fat Loss (FL)")
    app.progress_var.set(75)
    app.save_client()

    assert "info" in called
    assert "Senthil" in called["info"][1]
    assert "75%" in called["info"][1]
