import customtkinter as ctk
from config import *
from PIL import Image
import os

class SelectionFrame(ctk.CTkFrame):
    def __init__(self, master, current_user, on_select_dashboard, on_select_knowledge, on_select_tracker, on_select_analytics, on_select_chatbot, on_select_history, on_logout):
        super().__init__(master, fg_color=COLOR_BG_MAIN)
        self.current_user = current_user
        
        # Grid config
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header = ctk.CTkFrame(self, height=120, fg_color=COLOR_PRIMARY, corner_radius=0)
        self.header.grid(row=0, column=0, sticky="nsew")
        
        title_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        title_frame.pack(side="left", padx=50, pady=20)
        
        welcome_text = f"WELCOME, {current_user.upper()}" if current_user else "WELCOME, GUEST"
        self.title_label = ctk.CTkLabel(title_frame, text=welcome_text, 
                                        font=ctk.CTkFont(family="Inter", size=32, weight="bold"), 
                                        text_color="white")
        self.title_label.pack(anchor="w")
        
        self.subtitle_label = ctk.CTkLabel(title_frame, text="Please select an option from the modules below:", 
                                        font=ctk.CTkFont(size=16), text_color="#E2E8F0")
        self.subtitle_label.pack(anchor="w", pady=(5, 0))

        self.logout_btn = ctk.CTkButton(self.header, text="Logout", width=120, height=40, 
                                        fg_color="transparent", border_width=2, border_color="white",
                                        hover_color="#1D4ED8", command=on_logout,
                                        font=ctk.CTkFont(size=14, weight="bold"))
        self.logout_btn.pack(side="right", padx=50, pady=30)

        # Content
        self.content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew", padx=60, pady=40)
        
        # 3x2 Grid for selection cards (only configure columns so rows can expand naturally)
        self.content.grid_columnconfigure((0, 1, 2), weight=1)

        self.asset_dir = os.path.join(os.path.dirname(__file__), "..", "assets")

        self.create_card(0, 0, "Diabetes Diagnostic Dashboard", "dashboard_icon.png", "Analyze patient data and get AI-powered diagnosis.", COLOR_PRIMARY, on_select_dashboard)
        self.create_card(0, 1, "Knowledgebase", "knowledgebase_icon.png", "Explore detailed information about diabetes and WHO guidelines.", COLOR_TEXT_MID, on_select_knowledge)
        
        # Health Tracker only for logged in users
        tracker_cmd = on_select_tracker if current_user else self.show_guest_warning
        self.create_card(0, 2, "Health Tracker", "tracker_icon.png", "Track glucose levels and BMI over time with personal history.", COLOR_VALID, tracker_cmd)
        
        self.create_card(1, 0, "Model Stats", "stats_icon.png", "View model performance, accuracy, and dataset insights.", "#F59E0B", on_select_analytics)

        # AI Chatbot Module
        self.create_card(1, 1, "AI Chatbot", "chatbot_icon.png", "Chat with our AI specialized in diabetes for quick answers.", "#8B5CF6", on_select_chatbot)

        # Diagnosis History Module
        history_cmd = on_select_history if current_user else self.show_guest_warning_history
        self.create_card(1, 2, "Diagnosis History", "history_icon.png", "View your past diagnosis reports and health stats.", "#10B981", history_cmd)

    def create_card(self, row, col, title, image_name, desc, accent_color, command):
        card = ctk.CTkFrame(self.content, fg_color=COLOR_BG_CARD, corner_radius=20, border_width=2, border_color=COLOR_BORDER, cursor="hand2")
        card.grid(row=row, column=col, sticky="nsew", padx=15, pady=15)
        
        def on_click(event=None):
            orig_color = card.cget("fg_color")
            orig_border = card.cget("border_color")
            card.configure(fg_color="#E2E8F0", border_color=accent_color)
            def execute():
                card.configure(fg_color=orig_color, border_color=orig_border)
                command()
            card.after(150, execute)

        card.bind("<Button-1>", on_click)

        try:
            img_path = os.path.join(self.asset_dir, image_name)
            pil_img = Image.open(img_path)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(70, 70))
            icon_label = ctk.CTkLabel(card, text="", image=ctk_img, fg_color=COLOR_BG_CARD)
            icon_label._image_ref = ctk_img  # keep reference to avoid garbage collection
            icon_label.pack(pady=(15, 5))
            icon_label.bind("<Button-1>", on_click)
        except Exception as e:
            # Fallback if image not found
            icon_label = ctk.CTkLabel(card, text="🖼️", font=ctk.CTkFont(size=50))
            icon_label.pack(pady=(20, 5))
            icon_label.bind("<Button-1>", on_click)
        
        title_label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_TEXT_DEEP, wraplength=200)
        title_label.pack(pady=5)
        title_label.bind("<Button-1>", on_click)
        
        desc_label = ctk.CTkLabel(card, text=desc, font=ctk.CTkFont(size=12), text_color=COLOR_TEXT_MID, wraplength=220)
        desc_label.pack(pady=(0, 10), padx=20)
        desc_label.bind("<Button-1>", on_click)
        
        btn_text = f"OPEN {title.upper()}"
        btn = ctk.CTkButton(card, text=btn_text, width=200, height=35, corner_radius=10, 
                             fg_color=accent_color, hover_color=COLOR_PRIMARY_HOVER,
                             command=on_click, font=ctk.CTkFont(size=12, weight="bold"))
        btn.pack(pady=(5, 15))

    def show_guest_warning(self):
        from tkinter import messagebox
        messagebox.showinfo("Access Restricted", "Health Tracker is only available for registered users. Please sign up to track your health data.")

    def show_guest_warning_history(self):
        from tkinter import messagebox
        messagebox.showinfo("Access Restricted", "Diagnosis History is only available for registered users. Please sign up to save and view history.")
