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

    # Flush any pending events before destroying the root
    root.update_idletasks()
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

def test_save_client_adds_to_clients_and_table(monkeypatch, app):
    """Ensure save_client adds client to list and table."""
    called = {}
    def fake_info(title, message):
        called["info"] = (title, message)
    monkeypatch.setattr("aceest_app.messagebox.showinfo", fake_info)

    app.name_var.set("TestUser")
    app.age_var.set(28)
    app.weight_var.set(72)
    app.program_var.set("Beginner (BG)")
    app.progress_var.set(60)
    app.notes_var.set("Consistent")

    app.save_client()

    # Check client list updated
    assert len(app.clients) == 1
    assert app.clients[0][0] == "TestUser"
    # Check table updated
    items = app.client_table.get_children()
    assert len(items) == 1
    values = app.client_table.item(items[0])["values"]
    assert values[0] == "TestUser"
    # Check info message called
    assert "info" in called

def test_export_csv_writes_file(monkeypatch, tmp_path, app):
    """Ensure export_csv writes client data to CSV file."""
    # Add a client
    app.clients.append(("A", 20, 60, "Beginner (BG)", 40, "Note"))
    fake_file = tmp_path / "clients.csv"

    def fake_saveasfilename(**kwargs):
        return str(fake_file)
    def fake_info(title, message):
        pass

    monkeypatch.setattr("aceest_app.filedialog.asksaveasfilename", fake_saveasfilename)
    monkeypatch.setattr("aceest_app.messagebox.showinfo", fake_info)

    app.export_csv()

    # Verify file contents
    lines = fake_file.read_text().splitlines()
    assert "Name,Age,Weight,Program,Adherence,Notes" in lines[0]
    assert "A,20,60,Beginner (BG),40,Note" in lines[1]

def test_export_csv_no_clients(monkeypatch, app):
    """Ensure export_csv warns when no clients exist."""
    called = {}
    def fake_warning(title, message):
        called["warning"] = (title, message)
    monkeypatch.setattr("aceest_app.messagebox.showwarning", fake_warning)

    app.export_csv()
    assert "warning" in called
    assert "No Data" in called["warning"][0]

def test_update_chart_draws_bars(app):
    """Ensure update_chart draws bars for clients."""
    app.clients.append(("A", 20, 60, "Beginner (BG)", 40, ""))
    app.clients.append(("B", 25, 70, "Fat Loss (FL)", 80, ""))
    app.update_chart()
    bars = app.ax.patches
    assert len(bars) == 2
    heights = [bar.get_height() for bar in bars]
    assert heights == [40, 80]
