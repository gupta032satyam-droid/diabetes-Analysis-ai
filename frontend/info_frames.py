import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime
import numpy as np
import os
from config import *

# Import medicines recommender
try:
    import medicine_recommender
    from patient_predict import LABEL_MAP
except ImportError:
    pass

class ResultFrame(ctk.CTkFrame):
    def __init__(self, master, result_data, on_back):
        super().__init__(master, fg_color=COLOR_BG_MAIN)
        self.result_data, self.on_back = result_data, on_back
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.back_btn = ctk.CTkButton(self.scroll_container, text="← Back to Dashboard", fg_color="transparent", text_color=COLOR_PRIMARY, font=ctk.CTkFont(weight="bold"), command=on_back)
        self.back_btn.pack(anchor="w", pady=(0, 20))

        is_positive = result_data["label"] == "No Diabetes"
        banner_color = COLOR_VALID if is_positive else "#F59E0B"
        self.banner = ctk.CTkFrame(self.scroll_container, fg_color=banner_color, corner_radius=20)
        self.banner.pack(fill="x", pady=10)
        ctk.CTkLabel(self.banner, text="🎉" if is_positive else "⚠️", font=ctk.CTkFont(size=60)).pack(pady=(20, 5))
        ctk.CTkLabel(self.banner, text="CONGRATULATIONS!" if is_positive else "DIAGNOSIS WARNING", font=ctk.CTkFont(size=28, weight="bold"), text_color="white").pack()
        ctk.CTkLabel(self.banner, text="No Diabetes Detected" if is_positive else f"{result_data['label']} Detected", font=ctk.CTkFont(size=20), text_color="white").pack(pady=(0, 20))

        if not is_positive: self.create_treatment_card()
        self.create_stats_panel()
        self.create_clinical_comparison_panel()
        ctk.CTkButton(self.scroll_container, text="Download Detailed Report (TXT)", height=50, fg_color=COLOR_PRIMARY, corner_radius=12, font=ctk.CTkFont(weight="bold"), command=self.export_report).pack(fill="x", pady=30)

    def create_treatment_card(self):
        card = ctk.CTkFrame(self.scroll_container, fg_color="white", corner_radius=20, border_width=1, border_color=COLOR_BORDER)
        card.pack(fill="x", pady=10, ipady=15)
        ctk.CTkLabel(card, text="🩺 Clinical Treatment Plan", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_TEXT_DEEP).pack(anchor="w", padx=25, pady=(15, 10))
        try:
            mapping = {"Pre-Diabetes": "Prediabetes", "Type 1 Diabetes": "Type 1", "Type 2 Diabetes": "Type 2", "Gestational Diabetes": "Gestational", "Child/Pediatric Type 1": "Type 1", "Child/Pediatric Type 2": "Type 2"}
            m_type = mapping.get(self.result_data["label"], "Type 2")
            rec = medicine_recommender.recommend(diabetes_type=m_type, age=self.result_data["raw_data"]["age"], bmi=self.result_data["raw_data"]["bmi"], hba1c=self.result_data["raw_data"]["hba1c"], blood_glucose=self.result_data["raw_data"]["glucose"], gender=self.result_data["raw_data"]["gender"])
            self.add_info_row(card, "💊 Recommended Medicine", rec["medicine"])
            self.add_info_row(card, "⚖️ Dosage Guideline", rec["dosage"])
            self.add_info_row(card, "🥗 Dietary Advice", rec["diet"])
            self.add_info_row(card, "⚠️ Precautions", rec["precautions"])
        except Exception as e: ctk.CTkLabel(card, text=f"Medication info unavailable: {e}", text_color="gray").pack(padx=25)

    def add_info_row(self, parent, label, value):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=25, pady=5)
        ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=13, weight="bold"), text_color=COLOR_TEXT_MID).pack(side="left")
        ctk.CTkLabel(row, text=value, font=ctk.CTkFont(size=13), text_color=COLOR_TEXT_DEEP, wraplength=600, justify="left").pack(side="right", padx=10)

    def create_stats_panel(self):
        panel = ctk.CTkFrame(self.scroll_container, fg_color="white", corner_radius=20, border_width=1, border_color=COLOR_BORDER)
        panel.pack(fill="x", pady=10, ipady=15)
        ctk.CTkLabel(panel, text="📊 AI Model Confidence Scores", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_TEXT_DEEP).pack(anchor="w", padx=25, pady=(15, 10))
        proba = self.result_data["all_proba"]
        for idx in np.argsort(proba)[::-1]:
            if proba[idx] < 0.01: continue
            name = LABEL_MAP.get(idx, "Unknown")
            frame = ctk.CTkFrame(panel, fg_color="transparent")
            frame.pack(fill="x", padx=25, pady=8)
            ctk.CTkLabel(frame, text=name, font=ctk.CTkFont(size=13), text_color=COLOR_TEXT_DEEP).pack(side="left")
            ctk.CTkLabel(frame, text=f"{proba[idx]*100:.1f}%", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLOR_PRIMARY).pack(side="right")
            bar = ctk.CTkProgressBar(panel, height=8, corner_radius=5, fg_color="#F1F5F9", progress_color=COLOR_PRIMARY)
            bar.pack(fill="x", padx=25, pady=(0, 10))
            bar.set(proba[idx])

    def create_clinical_comparison_panel(self):
        who_limits = {
            "bmi": {"name": "BMI", "normal": 24.9, "unit": "kg/m²", "max_scale": 40},
            "glucose": {"name": "Fasting Glucose", "normal": 99.0, "unit": "mg/dL", "max_scale": 200},
            "hba1c": {"name": "HbA1c", "normal": 5.7, "unit": "%", "max_scale": 12},
            "cholesterol": {"name": "Total Cholesterol", "normal": 200.0, "unit": "mg/dL", "max_scale": 300},
            "insulin": {"name": "Insulin", "normal": 25.0, "unit": "uIU/mL", "max_scale": 50}
        }
        
        exceeded = []
        for key, limits in who_limits.items():
            val = self.result_data["raw_data"].get(key, -1)
            if val != -1 and val > limits["normal"]:
                exceeded.append((key, val, limits))
                
        if not exceeded:
            return
            
        panel = ctk.CTkFrame(self.scroll_container, fg_color="white", corner_radius=20, border_width=1, border_color=COLOR_BORDER)
        panel.pack(fill="x", pady=10, ipady=15)
        
        header_frame = ctk.CTkFrame(panel, fg_color="transparent")
        header_frame.pack(fill="x", padx=25, pady=(15, 5))
        
        ctk.CTkLabel(header_frame, text="📈 WHO Clinical Threshold Analysis", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_TEXT_DEEP).pack(side="left")
        ctk.CTkLabel(header_frame, text="(Values exceeding normal ranges)", font=ctk.CTkFont(size=13), text_color="#EF4444").pack(side="left", padx=10, pady=(4,0))
        
        for key, val, limits in exceeded:
            frame = ctk.CTkFrame(panel, fg_color="transparent")
            frame.pack(fill="x", padx=25, pady=10)
            
            info_frame = ctk.CTkFrame(frame, fg_color="transparent")
            info_frame.pack(fill="x", pady=(0, 5))
            
            name_lbl = ctk.CTkLabel(info_frame, text=limits["name"], font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_TEXT_DEEP)
            name_lbl.pack(side="left")
            
            diff = val - limits["normal"]
            val_text = f"+{diff:.1f} {limits['unit']} above normal"
            val_lbl = ctk.CTkLabel(info_frame, text=val_text, font=ctk.CTkFont(size=13, weight="bold"), text_color="#EF4444")
            val_lbl.pack(side="right")
            
            scale_max = max(limits["max_scale"], val * 1.2)
            normal_progress = limits["normal"] / scale_max
            user_progress = val / scale_max
            
            normal_frame = ctk.CTkFrame(frame, fg_color="transparent")
            normal_frame.pack(fill="x", pady=2)
            ctk.CTkLabel(normal_frame, text="Normal Limit", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT_MID, width=80, anchor="w").pack(side="left")
            normal_bar = ctk.CTkProgressBar(normal_frame, height=10, fg_color="#F1F5F9", progress_color=COLOR_VALID)
            normal_bar.pack(side="left", fill="x", expand=True, padx=10)
            normal_bar.set(normal_progress)
            ctk.CTkLabel(normal_frame, text=f"≤ {limits['normal']}", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT_MID, width=50, anchor="e").pack(side="right")
            
            user_frame = ctk.CTkFrame(frame, fg_color="transparent")
            user_frame.pack(fill="x", pady=2)
            ctk.CTkLabel(user_frame, text="Your Level", font=ctk.CTkFont(size=12, weight="bold"), text_color="#EF4444", width=80, anchor="w").pack(side="left")
            user_bar = ctk.CTkProgressBar(user_frame, height=10, fg_color="#F1F5F9", progress_color="#EF4444")
            user_bar.pack(side="left", fill="x", expand=True, padx=10)
            user_bar.set(user_progress)
            ctk.CTkLabel(user_frame, text=f"{val}", font=ctk.CTkFont(size=12, weight="bold"), text_color="#EF4444", width=50, anchor="e").pack(side="right")

    def export_report(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], initialfile=f"Diabetes_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("="*50 + "\n      DIABETES DIAGNOSE AI - MEDICAL REPORT\n" + "="*50 + "\n\n")
                f.write(f"Date: {datetime.now()}\nDiagnosis: {self.result_data['label']}\nConfidence: {self.result_data['confidence']:.2f}%\n\nPatient Metrics:\n")
                for k, v in self.result_data["raw_data"].items(): f.write(f"- {k.replace('_', ' ').title()}: {v}\n")
            messagebox.showinfo("Saved", f"Report saved to {file_path}")

class KnowledgeFrame(ctk.CTkFrame):
    DIABETES_DETAILS = {
        "Type 1 Diabetes": {
            "icon": "💉",
            "subtitle": "Autoimmune Condition",
            "description": "An autoimmune reaction where the body's immune system destroys the cells in the pancreas that make insulin.",
            "stats": [
                ("Global Prevalence", "Approx. 9 million people", 0.15),
                ("Daily Management", "100% insulin dependent", 1.0),
                ("Diagnosis Rate", "Increasing 3% annually", 0.3)
            ],
            "who_fact": "WHO estimates that Type 1 diabetes cannot currently be prevented.",
            "sections": [
                ("⚠️ Common Symptoms", [
                    "Polydipsia (Excessive thirst)",
                    "Polyuria (Frequent urination)",
                    "Unintentional weight loss",
                    "Constant hunger",
                    "Extreme fatigue & blurred vision"
                ]),
                ("🧬 Possible Causes", [
                    "Autoimmune reaction: immune system attacks beta cells",
                    "Genetic predisposition",
                    "Environmental triggers (viruses)"
                ]),
                ("🛡️ Clinical Management", [
                    "Daily insulin therapy (injections or pump)",
                    "Continuous Blood Glucose Monitoring",
                    "Structured diet & physical activity"
                ]),
                ("❗ Long-term Risks", [
                    "Cardiovascular disease",
                    "Nerve damage (Neuropathy)",
                    "Kidney failure (Nephropathy)",
                    "Vision loss (Retinopathy)"
                ])
            ]
        },
        "Type 2 Diabetes": {
            "icon": "🍎",
            "subtitle": "Metabolic Condition",
            "description": "The body becomes resistant to insulin or fails to produce enough, leading to high blood sugar levels.",
            "stats": [
                ("Global Cases", "Over 95% of all diabetes", 0.95),
                ("Preventability", "Up to 80% preventable", 0.8),
                ("Low-Income Impact", "80% of cases in LMICs", 0.8)
            ],
            "who_fact": "Healthy diet, regular physical activity, and maintaining a normal body weight can prevent Type 2.",
            "sections": [
                ("⚠️ Common Symptoms", [
                    "Often asymptomatic for years",
                    "Slow-healing sores",
                    "Frequent infections",
                    "Darkened skin (Acanthosis nigricans)"
                ]),
                ("🧬 Risk Factors", [
                    "Excess body weight & obesity",
                    "Physical inactivity",
                    "Genetics & family history",
                    "Increasing age"
                ]),
                ("🛡️ Management", [
                    "Lifestyle modification (Diet/Exercise)",
                    "Oral medications (e.g., Metformin)",
                    "Insulin therapy (in advanced stages)"
                ]),
                ("❗ Complications", [
                    "Heart attack & Stroke",
                    "Lower limb amputation risk",
                    "Chronic Kidney Disease"
                ])
            ]
        },
        "Pre-Diabetes": {
            "icon": "📈",
            "subtitle": "Warning Stage",
            "description": "Blood sugar levels are higher than normal but not yet high enough for a diabetes diagnosis.",
            "stats": [
                ("Risk Level", "High risk of Type 2", 0.7),
                ("Reversibility", "High with lifestyle change", 0.85),
                ("Awareness", "80% don't know they have it", 0.2)
            ],
            "who_fact": "Intervention at this stage can prevent the progression to Type 2 diabetes.",
            "sections": [
                ("🔍 Key Indicators", [
                    "Fasting glucose: 100-125 mg/dL",
                    "HbA1c: 5.7% to 6.4%",
                    "No clear symptoms usually present"
                ]),
                ("⚡ Reversal Steps", [
                    "Lose 5-10% of body weight",
                    "150 minutes of weekly activity",
                    "Reduce processed sugar intake"
                ])
            ]
        },
        "Gestational Diabetes": {
            "icon": "🤰",
            "subtitle": "Pregnancy-Related",
            "description": "Hyperglycemia with blood glucose values above normal but below those diagnostic of diabetes, during pregnancy.",
            "stats": [
                ("Pregnancy Impact", "Affects 2-10% globally", 0.1),
                ("Future Risk (Mother)", "50% risk of Type 2", 0.5),
                ("Future Risk (Child)", "Higher obesity risk", 0.4)
            ],
            "who_fact": "Managing blood sugar during pregnancy is vital for the health of both mother and child.",
            "sections": [
                ("🩺 Care Plan", [
                    "Specialized prenatal nutrition",
                    "Regular glucose monitoring",
                    "Post-partum screening at 6-12 weeks"
                ]),
                ("👶 Impact on Baby", [
                    "Excessive birth weight (Macrosomia)",
                    "Preterm birth risks",
                    "Low blood sugar at birth"
                ])
            ]
        },
        "Pediatric Type 1": {
            "icon": "👶",
            "subtitle": "Childhood Onset T1",
            "description": "The most common form of diabetes in children, requiring lifelong management from a young age.",
            "stats": [
                ("Growth Rate", "Incidence rising globally", 0.4),
                ("Care Intensity", "Requires 24/7 monitoring", 1.0),
                ("Early Detection", "Critical for safety", 0.9)
            ],
            "who_fact": "Early diagnosis is crucial to avoid life-threatening diabetic ketoacidosis (DKA).",
            "sections": [
                ("🏫 School Care", [
                    "Individualized Health Plan (IHP)",
                    "Staff training on insulin/glucagon",
                    "Freedom to snack & test glucose"
                ]),
                ("🎒 Daily Essentials", [
                    "Blood glucose meter & strips",
                    "Fast-acting glucose (for lows)",
                    "Backup insulin & syringes"
                ])
            ]
        },
        "Pediatric Type 2": {
            "icon": "🧒",
            "subtitle": "Childhood Onset T2",
            "description": "Increasingly common in children and adolescents, driven primarily by the obesity epidemic.",
            "stats": [
                ("Rising Concern", "Significant increase since 1990", 0.6),
                ("Primary Cause", "Associated with high BMI", 0.85),
                ("Silent Onset", "Often asymptomatic", 0.7)
            ],
            "who_fact": "Type 2 diabetes is no longer just an 'adult' disease.",
            "sections": [
                ("🏠 Family Focus", [
                    "Healthy eating for the whole family",
                    "Reducing screen time",
                    "Encouraging active play"
                ]),
                ("🩺 Screening", [
                    "Recommended for children with BMI > 85th percentile",
                    "Testing starts at age 10 or onset of puberty"
                ])
            ]
        }
    }

    def __init__(self, master, on_back):
        super().__init__(master, fg_color=COLOR_BG_MAIN)
        self.on_back_callback = on_back
        
        # Configure grid for proper expansion
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header = ctk.CTkFrame(self, height=80, fg_color=COLOR_PRIMARY, corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False) # Keep height fixed
        
        self.back_btn = ctk.CTkButton(self.header, text="← Back", width=80, height=35, fg_color="transparent", border_width=1, border_color="white", command=self.on_back_press)
        self.back_btn.pack(side="left", padx=20, pady=22)
        
        self.title_label = ctk.CTkLabel(self.header, text="DIABETES KNOWLEDGE BASE", font=ctk.CTkFont(size=20, weight="bold"), text_color="white")
        self.title_label.pack(side="left", padx=10, pady=20)

        # Main Scrollable Area (persistent)
        self.content_area = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.content_area.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self.current_view = None
        self.render_list()

    def on_back_press(self):
        if self.current_view == "detail":
            self.render_list()
        else:
            self.on_back_callback()

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def render_list(self):
        self.clear_content()
        self.current_view = "list"
        self.title_label.configure(text="DIABETES KNOWLEDGE BASE")
        
        # Container for list items to add padding
        list_container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        list_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        for title, info in self.DIABETES_DETAILS.items():
            card = ctk.CTkFrame(list_container, fg_color="white", corner_radius=15, border_width=1, border_color=COLOR_BORDER, cursor="hand2")
            card.pack(fill="x", pady=10, ipady=10)
            
            # Helper to bind click to all children
            def bind_click(w, t=title):
                w.bind("<Button-1>", lambda e: self.show_details(t))
                for child in w.winfo_children():
                    bind_click(child, t)
            
            icon_label = ctk.CTkLabel(card, text=info["icon"], font=ctk.CTkFont(size=40))
            icon_label.pack(side="left", padx=20)
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(side="left", fill="both", expand=True, padx=10)
            
            ctk.CTkLabel(inner, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_TEXT_DEEP).pack(anchor="w")
            ctk.CTkLabel(inner, text=info["description"], font=ctk.CTkFont(size=13), text_color=COLOR_TEXT_MID, wraplength=500, justify="left").pack(anchor="w")
            
            detail_label = ctk.CTkLabel(card, text="Details →", text_color=COLOR_PRIMARY, font=ctk.CTkFont(size=12, weight="bold"))
            detail_label.pack(side="right", padx=20)
            
            bind_click(card)

    def show_details(self, title):
        self.clear_content()
        self.current_view = "detail"
        info = self.DIABETES_DETAILS[title]
        self.title_label.configure(text=f"DETAILS: {title.upper()}")
        
        detail_container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        detail_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Hero Section
        hero = ctk.CTkFrame(detail_container, fg_color="white", corner_radius=20, border_width=1, border_color=COLOR_BORDER)
        hero.pack(fill="x", pady=(0, 20), ipady=20)
        
        header_row = ctk.CTkFrame(hero, fg_color="transparent")
        header_row.pack(fill="x", padx=30, pady=(20, 10))
        
        ctk.CTkLabel(header_row, text=info["icon"], font=ctk.CTkFont(size=60)).pack(side="left")
        
        title_box = ctk.CTkFrame(header_row, fg_color="transparent")
        title_box.pack(side="left", padx=20)
        ctk.CTkLabel(title_box, text=title, font=ctk.CTkFont(size=32, weight="bold"), text_color=COLOR_TEXT_DEEP).pack(anchor="w")
        ctk.CTkLabel(title_box, text=info["subtitle"], font=ctk.CTkFont(size=16), text_color=COLOR_PRIMARY).pack(anchor="w")
        
        ctk.CTkLabel(hero, text=info["description"], font=ctk.CTkFont(size=15), text_color=COLOR_TEXT_MID, wraplength=700, justify="left").pack(fill="x", padx=30, pady=10)
        
        # Stats Grid
        stats_frame = ctk.CTkFrame(detail_container, fg_color="transparent")
        stats_frame.pack(fill="x", pady=10)
        
        for i, (label, val, progress) in enumerate(info["stats"]):
            s_card = ctk.CTkFrame(stats_frame, fg_color="white", corner_radius=15, border_width=1, border_color=COLOR_BORDER, width=230, height=130)
            s_card.pack_propagate(False)
            s_card.pack(side="left", padx=(0 if i==0 else 15, 0), expand=True, fill="both")
            
            ctk.CTkLabel(s_card, text=label, font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MID).pack(pady=(15, 5))
            ctk.CTkLabel(s_card, text=val, font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_PRIMARY).pack()
            
            bar = ctk.CTkProgressBar(s_card, height=6, progress_color=COLOR_PRIMARY, fg_color="#E2E8F0")
            bar.pack(fill="x", padx=20, pady=15)
            bar.set(progress)

        # WHO Fact Banner
        who_banner = ctk.CTkFrame(detail_container, fg_color=COLOR_PRIMARY, corner_radius=15)
        who_banner.pack(fill="x", pady=20, ipady=15)
        ctk.CTkLabel(who_banner, text=f"🌐 WHO FACT: {info['who_fact']}", font=ctk.CTkFont(size=14, weight="bold"), text_color="white", wraplength=700).pack(padx=20)

        # Render New Sections
        if "sections" in info:
            for s_title, items in info["sections"]:
                section_card = ctk.CTkFrame(detail_container, fg_color="white", corner_radius=20, border_width=1, border_color=COLOR_BORDER)
                section_card.pack(fill="x", pady=10, ipady=15)
                
                ctk.CTkLabel(section_card, text=s_title, font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_TEXT_DEEP).pack(anchor="w", padx=30, pady=(15, 10))
                
                for item in items:
                    ctk.CTkLabel(section_card, text=f"• {item}", font=ctk.CTkFont(size=14), text_color=COLOR_TEXT_MID, wraplength=650, justify="left").pack(anchor="w", padx=45, pady=3)
        
        # Reset scroll to top
        self.content_area._parent_canvas.yview_moveto(0)

