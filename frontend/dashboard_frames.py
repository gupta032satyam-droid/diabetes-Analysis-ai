import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
import sys
import numpy as np
from datetime import datetime
from config import *

# Import prediction and DB logic
try:
    from patient_predict import build_features, LABEL_MAP, ALL_FEATURES, apply_clinical_logic
    import medicine_recommender
    import joblib
    
    # Add parent directory to sys.path to import from 'db' folder
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from db import auth_db
except ImportError:
    pass

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, on_back, on_logout, current_user=None):
        super().__init__(master, fg_color=COLOR_BG_MAIN)
        self.on_back = on_back
        self.on_logout = on_logout
        self.current_user = current_user
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── Header ────────────────────────────────────────
        self.header = ctk.CTkFrame(self, height=80, fg_color=COLOR_PRIMARY, corner_radius=0)
        self.header.grid(row=0, column=0, sticky="nsew")
        
        self.back_btn = ctk.CTkButton(self.header, text="← Back", width=80, height=35, 
                                       fg_color="transparent", border_width=2, border_color="white",
                                       hover_color="#1D4ED8", command=on_back)
        self.back_btn.pack(side="left", padx=20, pady=20)

        title_text = "DIABETES DIAGNOSTIC DASHBOARD"
        if self.current_user:
            title_text = f"WELCOME, {self.current_user.upper()}"

        self.header_title = ctk.CTkLabel(self.header, text=title_text, 
                                         font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
        self.header_title.pack(side="left", padx=10, pady=20)
        
        self.logout_btn = ctk.CTkButton(self.header, text="Logout", width=100, height=35, 
                                        fg_color="transparent", border_width=2, border_color="white",
                                        hover_color="#1D4ED8", command=on_logout)
        self.logout_btn.pack(side="right", padx=20, pady=20)

        # ── Main Content (Scrollable) ─────────────────────
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.scroll_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.create_form()

    def create_form(self):
        # Implementation of form sections...
        # (This is a large block of code from main_gui.py lines 184-318)
        self.vitals_card = self.create_card("Section 1: Vital Patient Information (Required)")
        self.inputs = {}
        self.inputs["age"] = self.create_input(self.vitals_card, "Age (Years)", "e.g. 45", required=True, validator=self.val_age)
        self.inputs["gender"] = self.create_dropdown(self.vitals_card, "Gender", ["Male", "Female", "Other"], required=True, callback=self.on_gender_change)
        self.inputs["bmi"] = self.create_input(self.vitals_card, "BMI (kg/m²)", "e.g. 24.5", required=True, validator=self.val_bmi)

        self.clinical_card = self.create_card("Section 2: Clinical Markers (Required)")
        self.inputs["glucose"] = self.create_input(self.clinical_card, "Fasting Glucose (mg/dL)", "e.g. 110", required=True, validator=self.val_glucose)
        self.inputs["hba1c"] = self.create_input(self.clinical_card, "HbA1c (%)", "e.g. 6.4", required=True, validator=self.val_hba1c)

        self.opt_card = self.create_card("Section 3: Additional Diagnostics (Optional)")
        bp_frame = ctk.CTkFrame(self.opt_card, fg_color="transparent")
        bp_frame.pack(fill="x", pady=5)
        self.inputs["systolic_bp"] = self.create_input(bp_frame, "Systolic BP", "mmHg", side="left", width=180)
        self.inputs["diastolic_bp"] = self.create_input(bp_frame, "Diastolic BP", "mmHg", side="left", width=180)
        self.inputs["cholesterol"] = self.create_input(self.opt_card, "Total Cholesterol", "mg/dL")
        self.inputs["insulin"] = self.create_input(self.opt_card, "Insulin Level", "uIU/mL")
        self.inputs["c_peptide"] = self.create_input(self.opt_card, "C-Peptide", "ng/mL")
        self.inputs["autoantibodies"] = self.create_dropdown(self.opt_card, "Autoantibody Test", ["Not Tested", "Positive", "Negative"])
        
        self.history_card = self.create_card("Section 4: History & Lifestyle (Optional)")
        self.inputs["family_history"] = self.create_dropdown(self.history_card, "Family History of Diabetes", ["No", "Yes", "Unknown"])
        self.inputs["hypertension"] = self.create_dropdown(self.history_card, "Hypertension?", ["No", "Yes", "Unknown"])
        self.inputs["heart_disease"] = self.create_dropdown(self.history_card, "Heart Disease History?", ["No", "Yes", "Unknown"])
        self.inputs["smoking"] = self.create_dropdown(self.history_card, "Smoking History", ["Non-smoker", "Current/Ex-smoker", "Unknown"])

        self.preg_card = self.create_card("Section 5: Pregnancy Context")
        self.preg_card.pack_forget() 
        self.inputs["is_pregnant"] = self.create_dropdown(self.preg_card, "Are you currently pregnant?", ["No", "Yes"], callback=self.on_preg_change)
        self.preg_details = ctk.CTkFrame(self.preg_card, fg_color="transparent")
        self.inputs["preg_week"] = self.create_input(self.preg_details, "Current Pregnancy Week", "e.g. 24")
        self.inputs["preg_count"] = self.create_input(self.preg_details, "Total Pregnancies", "e.g. 2")

        self.predict_btn = ctk.CTkButton(self.scroll_container, text="RUN AI DIAGNOSIS", height=60, 
                                          corner_radius=15, fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
                                          font=ctk.CTkFont(size=18, weight="bold"), command=self.run_prediction)
        self.predict_btn.pack(fill="x", pady=40, padx=20)

    def create_card(self, title):
        card = ctk.CTkFrame(self.scroll_container, fg_color="white", corner_radius=20, border_width=1, border_color=COLOR_BORDER)
        card.pack(fill="x", padx=20, pady=10, ipady=10)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_TEXT_DEEP).pack(anchor="w", padx=25, pady=(15, 10))
        return card

    def create_input(self, parent, label, placeholder, required=False, validator=None, side="top", width=380):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(side=side, fill="x" if side=="top" else "none", padx=25, pady=5)
        lbl_text = label + " *" if required else label
        ctk.CTkLabel(frame, text=lbl_text, font=ctk.CTkFont(size=13, weight="bold"), text_color=COLOR_TEXT_MID).pack(anchor="w")
        entry = ctk.CTkEntry(frame, width=width, height=45, corner_radius=10, border_width=2, fg_color="#F8FAFC", border_color=COLOR_BORDER, text_color=COLOR_TEXT_DEEP, placeholder_text=placeholder)
        entry.pack(pady=(2, 5), anchor="w")
        if validator:
            entry.bind("<KeyRelease>", lambda e: self.apply_validation(entry, validator))
        return entry

    def create_dropdown(self, parent, label, values, required=False, callback=None):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=25, pady=5)
        lbl_text = label + " *" if required else label
        ctk.CTkLabel(frame, text=lbl_text, font=ctk.CTkFont(size=13, weight="bold"), text_color=COLOR_TEXT_MID).pack(anchor="w")
        combo = ctk.CTkComboBox(frame, values=values, width=380, height=45, corner_radius=10, border_width=2, fg_color="#F8FAFC", border_color=COLOR_BORDER, text_color=COLOR_TEXT_DEEP, command=callback)
        combo.pack(pady=(2, 5), anchor="w")
        return combo

    def apply_validation(self, widget, validator):
        if validator(widget.get()): widget.configure(border_color=COLOR_VALID)
        else: widget.configure(border_color=COLOR_BORDER)

    def val_age(self, v): 
        try: return 0 < float(v) <= 120
        except: return False
    def val_bmi(self, v):
        try: return 5 < float(v) < 100
        except: return False
    def val_glucose(self, v):
        try: return 30 < float(v) < 700
        except: return False
    def val_hba1c(self, v):
        try: return 3.0 < float(v) < 20.0
        except: return False

    def on_gender_change(self, choice):
        if choice == "Female": self.preg_card.pack(fill="x", padx=20, pady=10, ipady=10, after=self.history_card)
        else: self.preg_card.pack_forget()

    def on_preg_change(self, choice):
        if choice == "Yes": self.preg_details.pack(fill="x")
        else: self.preg_details.pack_forget()

    def run_prediction(self):
        try:
            raw_data = {
                "age": float(self.inputs["age"].get()),
                "gender": self.inputs["gender"].get(),
                "bmi": float(self.inputs["bmi"].get()),
                "glucose": float(self.inputs["glucose"].get()),
                "hba1c": float(self.inputs["hba1c"].get()),
            }
        except ValueError:
            messagebox.showwarning("Incomplete Data", "Please fill in all required fields (*) with valid numbers.")
            return

        raw_data["systolic_bp"] = float(self.inputs["systolic_bp"].get()) if self.inputs["systolic_bp"].get() else -1
        raw_data["diastolic_bp"] = float(self.inputs["diastolic_bp"].get()) if self.inputs["diastolic_bp"].get() else -1
        raw_data["cholesterol"] = float(self.inputs["cholesterol"].get()) if self.inputs["cholesterol"].get() else -1
        raw_data["insulin"] = float(self.inputs["insulin"].get()) if self.inputs["insulin"].get() else -1
        raw_data["c_peptide_ng_ml"] = float(self.inputs["c_peptide"].get()) if self.inputs["c_peptide"].get() else -1
        
        ab_map = {"Not Tested": -1, "Positive": 1, "Negative": 0}
        raw_data["autoantibodies"] = ab_map.get(self.inputs["autoantibodies"].get(), -1)
        
        yn_map = {"No": 0, "Yes": 1, "Unknown": -1}
        raw_data["family_history_diabetes"] = yn_map.get(self.inputs["family_history"].get(), -1)
        raw_data["hypertension"] = yn_map.get(self.inputs["hypertension"].get(), -1)
        raw_data["heart_disease"] = yn_map.get(self.inputs["heart_disease"].get(), -1)
        
        smoke_map = {"Non-smoker": 0, "Current/Ex-smoker": 1, "Unknown": -1}
        raw_data["smoking_history"] = smoke_map.get(self.inputs["smoking"].get(), -1)

        if raw_data["gender"] == "Female" and self.inputs["is_pregnant"].get() == "Yes":
            raw_data["pregnancy_week"] = float(self.inputs["preg_week"].get()) if self.inputs["preg_week"].get() else -1
            raw_data["pregnancies"] = float(self.inputs["preg_count"].get()) if self.inputs["preg_count"].get() else -1
        else:
            raw_data["pregnancy_week"] = -1
            raw_data["pregnancies"] = -1

        MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "diabetes_rf_model.pkl")
        if not os.path.exists(MODEL_PATH):
            messagebox.showerror("Error", f"Model file '{MODEL_PATH}' not found.")
            return

        try:
            loaded = joblib.load(MODEL_PATH)
            if isinstance(loaded, dict) and "model" in loaded:
                model, model_features = loaded["model"], loaded.get("feature_cols")
            else:
                model, model_features = loaded, None

            X = build_features(raw_data, required_features=model_features)
            proba = model.predict_proba(X)[0]
            proba = apply_clinical_logic(proba, raw_data)

            pred_idx = int(np.argmax(proba))
            label = LABEL_MAP.get(pred_idx, "Unknown")
            final_results = {"label": label, "confidence": proba[pred_idx] * 100, "all_proba": proba, "raw_data": raw_data}
            
            # Save history if logged in
            if self.current_user:
                auth_db.save_diagnosis_history(
                    self.current_user,
                    label,
                    proba[pred_idx] * 100,
                    raw_data.get("bmi", -1),
                    raw_data.get("glucose", -1),
                    raw_data.get("hba1c", -1)
                )

            self.master.master.show_result(final_results)
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"An error occurred: {str(e)}")

class AnalyticsFrame(ctk.CTkFrame):
    def __init__(self, master, on_back):
        super().__init__(master, fg_color=COLOR_BG_MAIN)
        self.header = ctk.CTkFrame(self, height=80, fg_color=COLOR_PRIMARY, corner_radius=0)
        self.header.pack(fill="x")
        ctk.CTkButton(self.header, text="← Back", width=80, fg_color="transparent", border_width=1, border_color="white", command=on_back).pack(side="left", padx=20, pady=20)
        ctk.CTkLabel(self.header, text="MODEL ANALYTICS & DATASET INSIGHTS", font=ctk.CTkFont(size=20, weight="bold"), text_color="white").pack(side="left", padx=10)
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # Section 1: Classification Report
        self.create_section_title("📊 Model Performance Report")
        report_card = ctk.CTkFrame(self.scroll, fg_color="white", corner_radius=15, border_width=1, border_color=COLOR_BORDER)
        report_card.pack(fill="x", pady=10)
        report_path = os.path.join(os.path.dirname(__file__), "..", "trained_model1", "diabetes_classification_report.txt")
        report_text = "Report file not found."
        if os.path.exists(report_path):
            with open(report_path, "r") as f: report_text = f.read()
        ctk.CTkLabel(report_card, text=report_text, font=ctk.CTkFont(family="Courier", size=12), justify="left", text_color=COLOR_TEXT_DEEP, padx=20, pady=20).pack(anchor="w")

        # Section 2: Visuals
        self.create_section_title("📈 Visual Analytics")
        viz_container = ctk.CTkFrame(self.scroll, fg_color="transparent")
        viz_container.pack(fill="x", pady=10)
        model_dir = os.path.join(os.path.dirname(__file__), "..", "trained_model1")
        self.display_image(viz_container, os.path.join(model_dir, "feature_importance.png"), "Feature Importance")
        self.display_image(viz_container, os.path.join(model_dir, "confusion_matrix.png"), "Confusion Matrix")
        self.display_image(viz_container, os.path.join(model_dir, "dataset_distribution.png"), "Dataset Distribution")

        # Section 3: Dataset Info
        self.create_section_title("🗂️ Dataset Overview (finaldeta.csv)")
        stats_card = ctk.CTkFrame(self.scroll, fg_color="white", corner_radius=15, border_width=1, border_color=COLOR_BORDER)
        stats_card.pack(fill="x", pady=10, ipady=20)
        stats = [
            ("Total Records", "56,572 Cleaned Samples"), 
            ("No Diabetes", "42,137 Samples"),
            ("Type 2 Diabetes", "8,117 Samples"),
            ("Pre-Diabetes", "2,363 Samples"),
            ("Type 1 Diabetes", "1,500 Samples"),
            ("Gestational Diabetes", "1,430 Samples"),
            ("Child/Pediatric Type 1", "788 Samples"),
            ("Child/Pediatric Type 2", "237 Samples"),
            ("Age Range", "0 to 82 Years"), 
            ("Mean BMI", "27.86 kg/m²"), 
            ("Target Variable", "diabetes_type_name (7 Classes)")
        ]
        for label, val in stats:
            row = ctk.CTkFrame(stats_card, fg_color="transparent")
            row.pack(fill="x", padx=30, pady=5)
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_TEXT_MID).pack(side="left")
            ctk.CTkLabel(row, text=val, font=ctk.CTkFont(size=14), text_color=COLOR_TEXT_DEEP).pack(side="right")

    def create_section_title(self, title):
        ctk.CTkLabel(self.scroll, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_TEXT_DEEP).pack(anchor="w", padx=10, pady=(20, 5))

    def display_image(self, parent, path, title):
        if os.path.exists(path):
            card = ctk.CTkFrame(parent, fg_color="white", corner_radius=15, border_width=1, border_color=COLOR_BORDER)
            card.pack(side="left", padx=10, fill="both", expand=True)
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_TEXT_MID).pack(pady=10)
            try:
                img = Image.open(path)
                aspect = img.width / img.height
                w, h = 450, int(450 / aspect)
                ctk_img = ctk.CTkImage(light_image=img, size=(w, h))
                ctk.CTkLabel(card, image=ctk_img, text="").pack(padx=20, pady=10)
            except Exception as e: ctk.CTkLabel(card, text=f"Error: {e}", text_color="red").pack(pady=20)

class TrackerFrame(ctk.CTkFrame):
    def __init__(self, master, username, on_back):
        super().__init__(master, fg_color=COLOR_BG_MAIN)
        self.username, self.on_back = username, on_back
        self.header = ctk.CTkFrame(self, height=80, fg_color=COLOR_PRIMARY, corner_radius=0)
        self.header.pack(fill="x")
        ctk.CTkButton(self.header, text="← Back", width=80, fg_color="transparent", border_width=1, border_color="white", command=on_back).pack(side="left", padx=20, pady=20)
        ctk.CTkLabel(self.header, text="GLUCOSE & BMI PERSONAL TRACKER", font=ctk.CTkFont(size=20, weight="bold"), text_color="white").pack(side="left", padx=10)
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=20)

        card = ctk.CTkFrame(self.scroll, fg_color="white", corner_radius=20, border_width=1, border_color=COLOR_BORDER)
        card.pack(fill="x", pady=10, ipady=20)
        ctk.CTkLabel(card, text="Log Daily Measurements", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_TEXT_DEEP).pack(anchor="w", padx=30, pady=(20, 10))
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=30)
        self.g_entry = self.create_tracker_input(row, "Glucose (mg/dL)")
        self.b_entry = self.create_tracker_input(row, "BMI (kg/m²)")
        ctk.CTkButton(card, text="SAVE MEASUREMENTS", width=250, height=45, corner_radius=10, fg_color=COLOR_PRIMARY, command=self.save_data).pack(pady=25)
        self.history_container = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.history_container.pack(fill="x")
        self.refresh_history()

    def create_tracker_input(self, parent, label):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(side="left", padx=10)
        ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=13, weight="bold"), text_color=COLOR_TEXT_MID).pack(anchor="w")
        entry = ctk.CTkEntry(frame, width=200, height=45, corner_radius=10, border_width=2, border_color=COLOR_BORDER)
        entry.pack(pady=5)
        return entry

    def save_data(self):
        try:
            g, b = float(self.g_entry.get()), float(self.b_entry.get())
            success, msg = auth_db.save_vitals(self.username, g, b)
            if success:
                messagebox.showinfo("Saved", "Health data recorded.")
                self.g_entry.delete(0, "end"); self.b_entry.delete(0, "end")
                self.refresh_history()
            else: messagebox.showerror("Error", msg)
        except ValueError: messagebox.showwarning("Invalid", "Please enter numbers.")

    def refresh_history(self):
        for w in self.history_container.winfo_children(): w.destroy()
        history = auth_db.get_vitals_history(self.username)
        if not history:
            ctk.CTkLabel(self.history_container, text="No history yet.", text_color="gray").pack(pady=20)
            return
        header = ctk.CTkFrame(self.history_container, fg_color=COLOR_BORDER, height=40, corner_radius=10)
        header.pack(fill="x", pady=2)
        ctk.CTkLabel(header, text="Date & Time", width=250).pack(side="left", padx=10)
        ctk.CTkLabel(header, text="Glucose", width=150).pack(side="left", padx=10)
        ctk.CTkLabel(header, text="BMI", width=150).pack(side="left", padx=10)

        for g, b, dt in history:
            row = ctk.CTkFrame(self.history_container, fg_color="white", height=45, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=dt, width=250).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=str(g), width=150, text_color=COLOR_VALID if 70<=g<=140 else "#F59E0B").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"{b:.1f}", width=150, text_color=COLOR_VALID if 18.5<=b<=25 else "#F59E0B").pack(side="left", padx=10)

class DiagnosisHistoryFrame(ctk.CTkFrame):
    def __init__(self, master, username, on_back):
        super().__init__(master, fg_color=COLOR_BG_MAIN)
        self.username = username
        self.on_back = on_back

        self.header = ctk.CTkFrame(self, height=80, fg_color=COLOR_PRIMARY, corner_radius=0)
        self.header.pack(fill="x")
        
        ctk.CTkButton(self.header, text="← Back", width=80, fg_color="transparent", border_width=1, border_color="white", command=on_back).pack(side="left", padx=20, pady=20)
        ctk.CTkLabel(self.header, text="PATIENT DIAGNOSIS HISTORY", font=ctk.CTkFont(size=20, weight="bold"), text_color="white").pack(side="left", padx=10)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=20)

        self.load_history()

    def load_history(self):
        records = auth_db.get_diagnosis_history(self.username)
        
        # Summary Header
        summary_card = ctk.CTkFrame(self.scroll, fg_color="white", corner_radius=15, border_width=1, border_color=COLOR_BORDER)
        summary_card.pack(fill="x", pady=(0, 20), ipady=15)
        
        ctk.CTkLabel(summary_card, text=f"Total Diagnostic Checks: {len(records)}", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_TEXT_DEEP).pack(pady=10)

        if not records:
            ctk.CTkLabel(self.scroll, text="No diagnostic history found. Please run a diagnosis from the dashboard.", font=ctk.CTkFont(size=14), text_color=COLOR_TEXT_MID).pack(pady=30)
            return

        for label, conf, bmi, gl, hb, dt in records:
            card = ctk.CTkFrame(self.scroll, fg_color="white", corner_radius=15, border_width=1, border_color=COLOR_BORDER)
            card.pack(fill="x", pady=10, ipady=10)
            
            # Header of card
            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=20, pady=10)
            
            # Format datetime safely
            try:
                # Assuming format like "2026-05-16 10:30:00"
                dt_obj = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
                dt_str = dt_obj.strftime("%d %b %Y, %I:%M %p")
            except:
                dt_str = dt

            ctk.CTkLabel(header, text=dt_str, font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_TEXT_MID).pack(side="left")
            
            is_positive = (label == "No Diabetes")
            lbl_color = COLOR_VALID if is_positive else "#F59E0B"
            ctk.CTkLabel(header, text=f"{label} ({conf:.1f}%)", font=ctk.CTkFont(size=16, weight="bold"), text_color=lbl_color).pack(side="right")
            
            # Body stats
            stats_frame = ctk.CTkFrame(card, fg_color="transparent")
            stats_frame.pack(fill="x", padx=20, pady=5)
            
            def add_stat(parent, name, val, unit):
                f = ctk.CTkFrame(parent, fg_color="#F8FAFC", corner_radius=8, border_width=1, border_color=COLOR_BORDER)
                f.pack(side="left", fill="x", expand=True, padx=5)
                ctk.CTkLabel(f, text=name, font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MID).pack(pady=(5,0))
                ctk.CTkLabel(f, text=f"{val} {unit}" if val != -1 else "N/A", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_TEXT_DEEP).pack(pady=(0,5))
                
            add_stat(stats_frame, "BMI", bmi, "kg/m²")
            add_stat(stats_frame, "Glucose", gl, "mg/dL")
            add_stat(stats_frame, "HbA1c", hb, "%")
