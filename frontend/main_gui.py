import customtkinter as ctk
import os
import sys

# Add parent directory to sys.path to import from root and 'db' folder
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config import *
from auth_frames import LoginFrame, SignupFrame
from dashboard_frames import DashboardFrame, AnalyticsFrame, TrackerFrame, DiagnosisHistoryFrame
from info_frames import ResultFrame, KnowledgeFrame
from chatbot_frame import ChatbotFrame
from selection_frame import SelectionFrame

from db import auth_db

# Set appearance mode and color theme
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Initialize Database
        auth_db.initialize_db()

        self.current_user = None # Store logged-in username

        self.title("Diabetes Diagnose AI System")
        self.geometry("1000x800")
        self.resizable(True, True)

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        self.show_login()

    def show_login(self):
        self.current_user = None
        self.clear_frame()
        self.frames["login"] = LoginFrame(self.container, self.show_selection)
        self.frames["login"].pack(fill="both", expand=True)
        
        # Fade-in effect
        self.attributes('-alpha', 0.0)
        self.animate_fade_in()

    def show_signup(self):
        self.clear_frame()
        self.frames["signup"] = SignupFrame(self.container, self.show_login, self.show_login)
        self.frames["signup"].pack(fill="both", expand=True)

    def show_selection(self, user=None):
        self.current_user = user
        self.clear_frame()
        self.frames["selection"] = SelectionFrame(
            self.container, 
            self.current_user,
            self.show_dashboard_current,
            self.show_knowledge,
            self.show_tracker,
            self.show_analytics,
            self.show_chatbot,
            self.show_diagnosis_history,
            self.show_login
        )
        self.frames["selection"].pack(fill="both", expand=True)

    def show_dashboard(self, user=None):
        self.current_user = user
        self.clear_frame()
        self.frames["dashboard"] = DashboardFrame(self.container, self.show_selection_current, self.show_login, self.current_user)
        self.frames["dashboard"].pack(fill="both", expand=True)

    def show_result(self, result_data):
        self.clear_frame()
        self.frames["result"] = ResultFrame(self.container, result_data, self.show_dashboard_current)
        self.frames["result"].pack(fill="both", expand=True)

    def show_analytics(self):
        self.clear_frame()
        self.frames["analytics"] = AnalyticsFrame(self.container, self.show_selection_current)
        self.frames["analytics"].pack(fill="both", expand=True)

    def show_tracker(self):
        if self.current_user:
            self.clear_frame()
            self.frames["tracker"] = TrackerFrame(self.container, self.current_user, self.show_selection_current)
            self.frames["tracker"].pack(fill="both", expand=True)

    def show_diagnosis_history(self):
        if self.current_user:
            self.clear_frame()
            self.frames["history"] = DiagnosisHistoryFrame(self.container, self.current_user, self.show_selection_current)
            self.frames["history"].pack(fill="both", expand=True)

    def show_dashboard_current(self):
        """Helper to return to dashboard with current user state"""
        self.show_dashboard(self.current_user)

    def show_selection_current(self):
        """Helper to return to selection menu with current user state"""
        self.show_selection(self.current_user)

    def show_knowledge(self):
        self.clear_frame()
        self.frames["knowledge"] = KnowledgeFrame(self.container, self.show_selection_current)
        self.frames["knowledge"].pack(fill="both", expand=True)

    def show_chatbot(self):
        self.clear_frame()
        self.frames["chatbot"] = ChatbotFrame(self.container, self.show_selection_current)
        self.frames["chatbot"].pack(fill="both", expand=True)

    def clear_frame(self):
        """Destroy all existing frames to ensure a clean state for the next page."""
        for frame in self.frames.values():
            frame.destroy()
        self.frames.clear()

    def animate_fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            alpha += 0.05
            self.attributes("-alpha", alpha)
            self.after(20, self.animate_fade_in)

if __name__ == "__main__":
    app = App()
    app.mainloop()
