import customtkinter as ctk
from tkinter import messagebox
from config import *
import os
import sys

# Add parent directory to sys.path to import from 'db' folder
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db import auth_db

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, on_login):
        super().__init__(master, fg_color="transparent")
        self.on_login = on_login

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Left Frame (Branding & Stats) ──────────────────
        self.left_frame = ctk.CTkFrame(self, width=420, corner_radius=0, fg_color=COLOR_PRIMARY)
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        
        self.circle_deco = ctk.CTkLabel(self.left_frame, text="●", font=ctk.CTkFont(size=400), text_color="#3B82F6")
        self.circle_deco.place(relx=-0.1, rely=-0.1)

        self.logo_label = ctk.CTkLabel(self.left_frame, text="🩺", font=ctk.CTkFont(size=100))
        self.logo_label.place(relx=0.5, rely=0.28, anchor="center")

        self.title_label = ctk.CTkLabel(self.left_frame, text="DIABETES\nDIAGNOSE AI", 
                                        font=ctk.CTkFont(family="Inter", size=42, weight="bold"), 
                                        text_color="white")
        self.title_label.place(relx=0.5, rely=0.48, anchor="center")

        self.rf_label = ctk.CTkLabel(self.left_frame, text="RANDOM FOREST MODEL", 
                                     font=ctk.CTkFont(family="Inter", size=14, weight="bold"), text_color="#DBEAFE")
        self.rf_label.place(relx=0.5, rely=0.58, anchor="center")

        self.accuracy_card = ctk.CTkFrame(self.left_frame, fg_color="white", corner_radius=15)
        self.accuracy_card.place(relx=0.5, rely=0.7, anchor="center")
        
        self.acc_val_label = ctk.CTkLabel(self.accuracy_card, text="97.68%", 
                                          font=ctk.CTkFont(family="Inter", size=24, weight="bold"), 
                                          text_color=COLOR_PRIMARY, padx=20, pady=5)
        self.acc_val_label.pack()
        
        self.acc_text_label = ctk.CTkLabel(self.left_frame, text="Validated Clinical Accuracy", 
                                           font=ctk.CTkFont(size=12, weight="bold"), text_color="white")
        self.acc_text_label.place(relx=0.5, rely=0.78, anchor="center")

        self.footer_label = ctk.CTkLabel(self.left_frame, text="Developed by - Satyam Kumar Gupta", 
                                         font=ctk.CTkFont(size=11, weight="bold"), text_color="#BFDBFE")
        self.footer_label.place(relx=0.5, rely=0.94, anchor="center")

        # ── Right Frame (Form) ─────────────────────
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.grid(row=0, column=1, sticky="nsew")
        self.right_container.grid_columnconfigure(0, weight=1)
        self.right_container.grid_rowconfigure(0, weight=1)

        self.form_card = ctk.CTkFrame(self.right_container, corner_radius=30, fg_color=COLOR_BG_CARD, 
                                      border_width=2, border_color=COLOR_BORDER)
        self.form_card.grid(row=0, column=0, padx=60, pady=50, sticky="nsew")

        self.login_title = ctk.CTkLabel(self.form_card, text="SECURE ACCESS", 
                                        font=ctk.CTkFont(family="Inter", size=32, weight="bold"), 
                                        text_color=COLOR_TEXT_DEEP)
        self.login_title.pack(pady=(40, 10))

        self.sub_text = ctk.CTkLabel(self.form_card, text="Enter your credentials to begin diagnosis", 
                                     font=ctk.CTkFont(family="Inter", size=14, weight="bold"), 
                                     text_color=COLOR_TEXT_MID)
        self.sub_text.pack(pady=(0, 30))

        entry_style = {
            "width": 380, "height": 55, "corner_radius": 15, "border_width": 2, 
            "fg_color": "#F8FAFC", "border_color": COLOR_BORDER, 
            "text_color": COLOR_TEXT_DEEP, "placeholder_text_color": COLOR_TEXT_LIGHT
        }

        self.user_field = ctk.CTkEntry(self.form_card, placeholder_text="Username / Email", **entry_style)
        self.user_field.pack(pady=12)

        self.pass_field = ctk.CTkEntry(self.form_card, placeholder_text="Password", show="*", **entry_style)
        self.pass_field.pack(pady=12)

        self.forgot_btn = ctk.CTkLabel(self.form_card, text="Forgot Password?", 
                                       font=ctk.CTkFont(size=12, weight="bold"), 
                                       text_color=COLOR_PRIMARY, cursor="hand2")
        self.forgot_btn.pack(anchor="e", padx=100, pady=(0, 20))

        self.signin_btn = ctk.CTkButton(self.form_card, text="LOGIN SYSTEM", width=380, height=55, 
                                        corner_radius=15, fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
                                        command=self.login_event, 
                                        font=ctk.CTkFont(family="Inter", size=16, weight="bold"))
        self.signin_btn.pack(pady=10)

        self.div_box = ctk.CTkFrame(self.form_card, fg_color="transparent")
        self.div_box.pack(pady=20)
        ctk.CTkFrame(self.div_box, width=150, height=2, fg_color=COLOR_BORDER).grid(row=0, column=0)
        ctk.CTkLabel(self.div_box, text="OU", text_color=COLOR_TEXT_LIGHT, font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=15)
        ctk.CTkFrame(self.div_box, width=150, height=2, fg_color=COLOR_BORDER).grid(row=0, column=2)

        self.guest_hint = ctk.CTkLabel(self.form_card, text="Quick access for patient screening", 
                                       font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MID)
        self.guest_hint.pack(pady=(0, 5))

        self.guest_btn = ctk.CTkButton(self.form_card, text="GUEST ACCESS", 
                                       width=380, height=55, corner_radius=15, fg_color="transparent", 
                                       border_width=2, border_color=COLOR_PRIMARY,
                                       text_color=COLOR_PRIMARY, hover_color="#F0F7FF",
                                       command=lambda: self.on_login(None),
                                       font=ctk.CTkFont(family="Inter", size=15, weight="bold"))
        self.guest_btn.pack()

        self.signup_link = ctk.CTkLabel(self.form_card, text="Don't have an account? Create one", 
                                        font=ctk.CTkFont(size=12, weight="bold"), 
                                        text_color=COLOR_PRIMARY, cursor="hand2")
        self.signup_link.pack(pady=(15, 0))
        self.signup_link.bind("<Button-1>", lambda e: self.master.master.show_signup())

    def login_event(self):
        u = self.user_field.get()
        p = self.pass_field.get()
        
        if not u or not p:
            messagebox.showwarning("INPUT REQUIRED", "Please enter both username and password.")
            return

        success, message = auth_db.authenticate_user(u, p)
        if success:
            self.on_login(u)
        else:
            messagebox.showerror("ACCESS DENIED", message)

class SignupFrame(ctk.CTkFrame):
    def __init__(self, master, on_success, on_back):
        super().__init__(master, fg_color="transparent")
        self.on_success = on_success
        self.on_back = on_back

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Left Frame ──────────────────
        self.left_frame = ctk.CTkFrame(self, width=420, corner_radius=0, fg_color=COLOR_PRIMARY)
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.left_frame, text="📝", font=ctk.CTkFont(size=100))
        self.logo_label.place(relx=0.5, rely=0.35, anchor="center")

        self.title_label = ctk.CTkLabel(self.left_frame, text="JOIN US", 
                                        font=ctk.CTkFont(family="Inter", size=42, weight="bold"), 
                                        text_color="white")
        self.title_label.place(relx=0.5, rely=0.5, anchor="center")

        # ── Right Frame ─────────────────────
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.grid(row=0, column=1, sticky="nsew")
        self.right_container.grid_columnconfigure(0, weight=1)
        self.right_container.grid_rowconfigure(0, weight=1)

        self.form_card = ctk.CTkFrame(self.right_container, corner_radius=30, fg_color=COLOR_BG_CARD, 
                                      border_width=2, border_color=COLOR_BORDER)
        self.form_card.grid(row=0, column=0, padx=60, pady=50, sticky="nsew")

        self.back_btn = ctk.CTkButton(self.form_card, text="← Back to Login", 
                                       fg_color="transparent", text_color=COLOR_PRIMARY, 
                                       width=100, height=30, font=ctk.CTkFont(size=12, weight="bold"),
                                       command=on_back)
        self.back_btn.pack(anchor="w", padx=40, pady=(30, 0))

        self.signup_title = ctk.CTkLabel(self.form_card, text="CREATE ACCOUNT", 
                                         font=ctk.CTkFont(family="Inter", size=32, weight="bold"), 
                                         text_color=COLOR_TEXT_DEEP)
        self.signup_title.pack(pady=(20, 10))

        entry_style = {
            "width": 380, "height": 55, "corner_radius": 15, "border_width": 2, 
            "fg_color": "#F8FAFC", "border_color": COLOR_BORDER, 
            "text_color": COLOR_TEXT_DEEP, "placeholder_text_color": COLOR_TEXT_LIGHT
        }

        self.user_field = ctk.CTkEntry(self.form_card, placeholder_text="Choose Username", **entry_style)
        self.user_field.pack(pady=12)

        self.pass_field = ctk.CTkEntry(self.form_card, placeholder_text="Create Password", show="*", **entry_style)
        self.pass_field.pack(pady=12)

        self.confirm_pass_field = ctk.CTkEntry(self.form_card, placeholder_text="Confirm Password", show="*", **entry_style)
        self.confirm_pass_field.pack(pady=12)

        self.register_btn = ctk.CTkButton(self.form_card, text="REGISTER NOW", width=380, height=55, 
                                          corner_radius=15, fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
                                          command=self.signup_event, 
                                          font=ctk.CTkFont(family="Inter", size=16, weight="bold"))
        self.register_btn.pack(pady=30)

    def signup_event(self):
        u = self.user_field.get()
        p = self.pass_field.get()
        cp = self.confirm_pass_field.get()

        if not u or not p or not cp:
            messagebox.showwarning("INPUT REQUIRED", "Please fill in all fields.")
            return

        if p != cp:
            messagebox.showerror("PASSWORD MISMATCH", "Passwords do not match. Please try again.")
            return

        if len(p) < 6:
            messagebox.showwarning("WEAK PASSWORD", "Password must be at least 6 characters long.")
            return

        success, message = auth_db.register_user(u, p)
        if success:
            messagebox.showinfo("SUCCESS", "Account created successfully! You can now log in.")
            self.on_success()
        else:
            messagebox.showerror("ERROR", message)
