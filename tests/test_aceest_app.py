import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import os
import sqlite3
import tkinter as tk
from tkinter import ttk
from unittest.mock import patch, MagicMock
import pytest

from aceest_app import ACEestApp, DB_NAME


@pytest.fixture
def mock_root():
    """Fixture to provide a hidden root Tk instance for UI testing."""
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def test_db():
    """Fixture to set up a fresh test database and clean up afterwards."""
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    yield DB_NAME
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)


@pytest.fixture
def app_instance(mock_root, test_db):
    """Fixture to initialize the app, bypassing login and initializing all required UI elements."""
    with patch.object(ACEestApp, "show_login_window", lambda self: None):
        app = ACEestApp(mock_root)
        app.init_db()
        app.setup_data()
        
        # Initialize UI variables normally created inside setup_ui()
        app.name = tk.StringVar()
        app.age = tk.IntVar()
        app.height = tk.DoubleVar()
        app.weight = tk.DoubleVar()
        app.program = tk.StringVar()
        app.membership_var = tk.StringVar()
        app.status_var = tk.StringVar(value="Ready")
        
        # Mock or initialize the Text summary widget so refresh_summary doesn't crash
        app.summary = MagicMock()
        
        return app


# ==========================================
# 1. Database Initialization Tests
# ==========================================
def test_init_db(app_instance):
    """Test if all required database tables are successfully created."""
    app_instance.cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    )
    tables = {row[0] for row in app_instance.cur.fetchall()}
    
    expected_tables = {"users", "clients", "progress", "workouts", "exercises", "metrics"}
    assert expected_tables.issubset(tables)


# ==========================================
# 2. Authentication / Login Tests
# ==========================================
def test_login_success(app_instance, mock_root):
    """Test successful login with default admin credentials."""
    app_instance.login_win = MagicMock()
    app_instance.username_var = tk.StringVar(value="admin")
    app_instance.password_var = tk.StringVar(value="admin")
    
    with patch.object(app_instance, "setup_ui") as mock_setup_ui, \
         patch.object(mock_root, "deiconify") as mock_deiconify:
        
        app_instance.login_user()
        
        assert app_instance.user_role == "Admin"
        assert app_instance.current_user == "admin"
        mock_setup_ui.assert_called_once()
        mock_deiconify.assert_called_once()


def test_login_failure(app_instance):
    """Test login failure with invalid credentials."""
    app_instance.username_var = tk.StringVar(value="wrong_user")
    app_instance.password_var = tk.StringVar(value="wrong_pass")
    
    with patch("tkinter.messagebox.showerror") as mock_showerror:
        app_instance.login_user()
        assert app_instance.user_role is None
        mock_showerror.assert_called_once()


def test_save_client_empty_name(app_instance):
    """Test validation error when saving a client with an empty name."""
    app_instance.name.set("")
    with patch("tkinter.messagebox.showerror") as mock_showerror:
        app_instance.save_client()
        mock_showerror.assert_called_once()


def test_generate_ai_program(app_instance):
    """Test AI program generation for a valid client and experience level."""
    app_instance.current_client = "John Doe"
    
    app_instance.cur.execute(
        "INSERT INTO clients (name, program) VALUES (?, ?)",
        ("John Doe", "Muscle Gain (MG) – PPL")
    )
    app_instance.conn.commit()

    with patch("tkinter.simpledialog.askstring", return_value="intermediate"), \
         patch("tkinter.messagebox.showinfo") as mock_showinfo:
        
        app_instance.program_tree = ttk.Treeview(
            app_instance.root, columns=("day", "exercise", "sets", "reps")
        )
        
        app_instance.generate_ai_program()
        
        children = app_instance.program_tree.get_children()
        assert len(children) > 0
        mock_showinfo.assert_called_once()


def test_generate_ai_program_invalid_experience(app_instance):
    """Test AI program generation failure on invalid experience level input."""
    app_instance.current_client = "John Doe"
    
    with patch("tkinter.simpledialog.askstring", return_value="expert"), \
         patch("tkinter.messagebox.showerror") as mock_showerror:
        
        app_instance.program_tree = ttk.Treeview(
            app_instance.root, columns=("day", "exercise", "sets", "reps")
        )
        app_instance.generate_ai_program()
        mock_showerror.assert_called_once()


def test_export_pdf_report(app_instance):
    """Test PDF generation execution for a selected client."""
    app_instance.current_client = "John Doe"
    
    app_instance.cur.execute(
        """
        INSERT INTO clients (name, age, height, weight, program, membership_expiry)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("John Doe", 25, 180.0, 80.0, "Beginner (BG)", "2027-12-31")
    )
    app_instance.conn.commit()

    pdf_filename = "John Doe_report.pdf"
    if os.path.exists(pdf_filename):
        os.remove(pdf_filename)

    with patch("tkinter.messagebox.showinfo") as mock_showinfo:
        app_instance.export_pdf_report()
        
        assert os.path.exists(pdf_filename)
        mock_showinfo.assert_called_once()

    if os.path.exists(pdf_filename):
        os.remove(pdf_filename)

