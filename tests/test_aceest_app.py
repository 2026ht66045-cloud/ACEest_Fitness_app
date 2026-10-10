import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest
import tkinter as tk
from tkinter import messagebox
import sqlite3
from aceest_app import ACEestApp

@pytest.fixture
def app(monkeypatch):
    """Fixture to create and destroy the Tkinter app safely in headless CI."""
    root = tk.Tk()
    root.withdraw()
    app = ACEestApp(root)

    # Mock messagebox functions
    monkeypatch.setattr(messagebox, "showinfo", lambda *a, **k: None)
    monkeypatch.setattr(messagebox, "showerror", lambda *a, **k: None)
    monkeypatch.setattr(messagebox, "showwarning", lambda *a, **k: None)

    # Mock plt.show
    import matplotlib.pyplot as plt
    monkeypatch.setattr(plt, "show", lambda *a, **k: None)

    yield app
    root.update_idletasks()
    root.destroy()


def test_programs_exist(app):
    assert "Fat Loss (FL) – 3 day" in app.programs
    assert "Muscle Gain (MG) – PPL" in app.programs

def test_save_client_and_load(app):
    app.name.set("TestUser")
    app.age.set(25)
    app.height.set(175)
    app.weight.set(70)
    app.program.set("Fat Loss (FL) – 3 day")
    app.target_weight.set(65)
    app.target_adherence.set(80)
    app.save_client()

    app.load_client()
    summary_text = app.summary.get("1.0", "end")
    assert "TestUser" in summary_text
    assert "Fat Loss (FL)" in summary_text
    assert "65" in summary_text

def test_save_client_without_name_or_program(app):
    app.name.set("")
    app.program.set("")
    app.save_client()  # Should trigger error but not crash

def test_save_client_duplicate_replaces(app):
    app.name.set("DupUser")
    app.age.set(20)
    app.weight.set(60)
    app.program.set("Beginner (BG)")
    app.save_client()

    app.weight.set(65)
    app.save_client()

    app.cur.execute("SELECT weight FROM clients WHERE name=?", ("DupUser",))
    row = app.cur.fetchone()
    assert row[0] == 65

def test_load_client_not_found(app):
    app.name.set("NonExistent")
    app.load_client()
    assert app.summary.get("1.0", "end").strip() == ""

def test_save_progress(app):
    app.name.set("ProgressUser")
    app.age.set(30)
    app.weight.set(80)
    app.program.set("Muscle Gain (MG) – PPL")
    app.save_client()

    app.adherence.set(85)
    app.save_progress()

    app.cur.execute("SELECT * FROM progress WHERE client_name=?", ("ProgressUser",))
    row = app.cur.fetchone()
    assert row is not None
    assert row[1] == "ProgressUser"
    assert row[3] == 85

def test_save_progress_without_client(app):
    app.name.set("")
    app.adherence.set(50)
    app.save_progress()
    app.cur.execute("SELECT * FROM progress WHERE client_name=?", ("",))
    row = app.cur.fetchone()
    assert row is not None
    assert row[3] == 50

def test_show_progress_chart_no_data(app):
    app.name.set("ChartUser")
    app.save_client()
    app.show_progress_chart()  # Should not crash

def test_show_weight_chart_no_data(app):
    app.name.set("WeightUser")
    app.save_client()
    app.show_weight_chart()  # Should not crash

def test_show_bmi_info_underweight(monkeypatch, app):
    called = {}
    def fake_info(title, message):
        called["info"] = message
    monkeypatch.setattr(messagebox, "showinfo", fake_info)

    app.name.set("BMIUser")
    app.height.set(180)
    app.weight.set(50)
    app.program.set("Beginner (BG)")
    app.save_client()
    app.show_bmi_info()

    assert "Underweight" in called["info"]

def test_show_bmi_info_normal(monkeypatch, app):
    called = {}
    def fake_info(title, message):
        called["info"] = message
    monkeypatch.setattr(messagebox, "showinfo", fake_info)

    app.name.set("BMIUser2")
    app.height.set(170)
    app.weight.set(65)
    app.program.set("Beginner (BG)")
    app.save_client()
    app.show_bmi_info()

    assert "Normal" in called["info"]

def test_show_bmi_info_overweight(monkeypatch, app):
    called = {}
    def fake_info(title, message):
        called["info"] = message
    monkeypatch.setattr(messagebox, "showinfo", fake_info)

    app.name.set("BMIUser3")
    app.height.set(165)
    app.weight.set(75)
    app.program.set("Beginner (BG)")
    app.save_client()
    app.show_bmi_info()

    assert "Overweight" in called["info"]

def test_show_bmi_info_obese(monkeypatch, app):
    called = {}
    def fake_info(title, message):
        called["info"] = message
    monkeypatch.setattr(messagebox, "showinfo", fake_info)

    app.name.set("BMIUser4")
    app.height.set(160)
    app.weight.set(95)
    app.program.set("Beginner (BG)")
    app.save_client()
    app.show_bmi_info()

    assert "Obese" in called["info"]
