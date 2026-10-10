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
    root.withdraw()  # Prevent GUI window from showing
    app = ACEestApp(root)

    # Mock messagebox functions to avoid GUI popups
    monkeypatch.setattr(messagebox, "showinfo", lambda *a, **k: None)
    monkeypatch.setattr(messagebox, "showerror", lambda *a, **k: None)
    monkeypatch.setattr(messagebox, "showwarning", lambda *a, **k: None)

    # Mock plt.show to avoid blocking
    import matplotlib.pyplot as plt
    monkeypatch.setattr(plt, "show", lambda *a, **k: None)

    yield app
    root.update_idletasks()
    root.destroy()

def test_programs_exist(app):
    assert set(app.programs.keys()) == {"Fat Loss (FL)", "Muscle Gain (MG)", "Beginner (BG)"}

def test_field_helper_creates_entry(app):
    parent = tk.Frame(app.root)
    var = tk.StringVar()
    app._field(parent, "TestLabel", var)
    children = parent.winfo_children()
    labels = [w for w in children if isinstance(w, tk.Label)]
    entries = [w for w in children if isinstance(w, tk.Entry)]
    assert any("TestLabel" in l.cget("text") for l in labels)
    assert len(entries) == 1

def test_save_client_and_load(app):
    app.name.set("TestUser")
    app.age.set(25)
    app.weight.set(70)
    app.program.set("Fat Loss (FL)")
    app.save_client()

    app.load_client()
    summary_text = app.summary.get("1.0", "end")
    assert "TestUser" in summary_text
    assert "Fat Loss (FL)" in summary_text
    assert "70" in summary_text

def test_save_client_without_name_or_program(app):
    app.name.set("")
    app.program.set("")
    app.save_client()  # Should not raise

def test_save_client_duplicate_replaces(app):
    app.name.set("DupUser")
    app.age.set(20)
    app.weight.set(60)
    app.program.set("Beginner (BG)")
    app.save_client()

    # Save again with different weight
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
    app.program.set("Muscle Gain (MG)")
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

def test_calorie_calculation(app):
    app.name.set("CalUser")
    app.age.set(40)
    app.weight.set(100)
    app.program.set("Muscle Gain (MG)")
    app.save_client()
    app.cur.execute("SELECT calories FROM clients WHERE name=?", ("CalUser",))
    row = app.cur.fetchone()
    assert row[0] == 100 * app.programs["Muscle Gain (MG)"]["factor"]

def test_show_progress_chart_no_client(monkeypatch, app):
    called = {}
    def fake_warning(title, message):
        called["warning"] = (title, message)
    monkeypatch.setattr(messagebox, "showwarning", fake_warning)

    app.name.set("")
    app.show_progress_chart()
    assert "warning" in called
    assert "Enter client name first" in called["warning"][1]

def test_show_progress_chart_no_data(monkeypatch, app):
    called = {}
    def fake_info(title, message):
        called["info"] = (title, message)
    monkeypatch.setattr(messagebox, "showinfo", fake_info)

    app.name.set("NoDataUser")
    app.show_progress_chart()
    assert "info" in called
    assert "No progress data available" in called["info"][1]

def test_show_progress_chart_with_data(app):
    app.name.set("ChartUser")
    app.age.set(22)
    app.weight.set(55)
    app.program.set("Beginner (BG)")
    app.save_client()

    app.adherence.set(40)
    app.save_progress()
    app.adherence.set(70)
    app.save_progress()

    # Should run without error (plt.show mocked)
    app.show_progress_chart()
