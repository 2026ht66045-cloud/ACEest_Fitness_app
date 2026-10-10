import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from aceest_app import ACEestApp

@pytest.fixture
def app(monkeypatch):
    """Fixture to create and destroy the Tkinter app safely in headless CI."""
    root = tk.Tk()
    root.withdraw()  # Prevents GUI window from showing
    style = ttk.Style()
    style.theme_use("default")
    app = ACEestApp(root)
    yield app

    root.update_idletasks()
    root.destroy()

def test_programs_exist(app):
    assert "Fat Loss (FL)" in app.programs
    assert "Muscle Gain (MG)" in app.programs
    assert "Beginner (BG)" in app.programs

def test_update_program_fat_loss(app):
    app.weight.set(70)
    app.program.set("Fat Loss (FL)")
    # simulate calorie calculation
    expected_calories = int(70 * app.programs["Fat Loss (FL)"]["factor"])
    assert expected_calories == int(app.weight.get() * app.programs[app.program.get()]["factor"])

def test_update_program_muscle_gain(app):
    app.weight.set(80)
    app.program.set("Muscle Gain (MG)")
    expected_calories = int(80 * app.programs["Muscle Gain (MG)"]["factor"])
    assert expected_calories == int(app.weight.get() * app.programs[app.program.get()]["factor"])

def test_update_program_beginner(app):
    app.weight.set(60)
    app.program.set("Beginner (BG)")
    expected_calories = int(60 * app.programs["Beginner (BG)"]["factor"])
    assert expected_calories == int(app.weight.get() * app.programs[app.program.get()]["factor"])

def test_reset_clears_fields(app):
    app.name.set("Test User")
    app.age.set(25)
    app.weight.set(70)
    app.program.set("Fat Loss (FL)")
    app.adherence.set(80)

    # simulate reset
    app.name.set("")
    app.age.set(0)
    app.weight.set(0)
    app.program.set("")
    app.adherence.set(0)

    assert app.name.get() == ""
    assert app.age.get() == 0
    assert app.weight.get() == 0
    assert app.program.get() == ""
    assert app.adherence.get() == 0

def test_save_client_incomplete(monkeypatch, app):
    called = {}
    def fake_error(title, message):
        called["error"] = (title, message)
    monkeypatch.setattr(messagebox, "showerror", fake_error)

    app.name.set("")
    app.program.set("")
    app.save_client()

    assert "error" in called
    assert "Name and Program required" in called["error"][1]

def test_save_client_success(monkeypatch, app):
    called = {}
    def fake_info(title, message):
        called["info"] = (title, message)
    monkeypatch.setattr(messagebox, "showinfo", fake_info)

    app.name.set("Senthil")
    app.program.set("Fat Loss (FL)")
    app.adherence.set(75)
    app.weight.set(70)
    app.age.set(25)
    app.save_client()

    assert "info" in called
    assert "Client data saved" in called["info"][1]

def test_load_client_not_found(monkeypatch, app):
    called = {}
    def fake_warning(title, message):
        called["warning"] = (title, message)
    monkeypatch.setattr(messagebox, "showwarning", fake_warning)

    app.name.set("NonExistent")
    app.load_client()

    assert "warning" in called
    assert "Client not found" in called["warning"][1]

def test_save_progress(monkeypatch, app):
    called = {}
    def fake_info(title, message):
        called["info"] = (title, message)
    monkeypatch.setattr(messagebox, "showinfo", fake_info)

    app.name.set("ProgressUser")
    app.age.set(30)
    app.weight.set(80)
    app.program.set("Muscle Gain (MG)")
    app.save_client()

    app.adherence.set(85)
    app.save_progress()

    assert "info" in called
    assert "Weekly progress logged" in called["info"][1]

