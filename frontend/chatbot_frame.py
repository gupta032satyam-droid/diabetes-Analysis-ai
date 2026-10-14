import customtkinter as ctk
from config import *
from diabetes_kb import find_best_answer

class ChatbotFrame(ctk.CTkFrame):
    def __init__(self, master, on_back):
        super().__init__(master, fg_color=COLOR_BG_MAIN)
        self.on_back = on_back

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header = ctk.CTkFrame(self, height=80, fg_color=COLOR_PRIMARY, corner_radius=0)
        self.header.grid(row=0, column=0, sticky="nsew")
        
        self.back_btn = ctk.CTkButton(self.header, text="← BACK TO MENU", width=150, height=35, 
                                        fg_color="transparent", border_width=2, border_color="white",
                                        hover_color=COLOR_PRIMARY_HOVER, command=on_back,
                                        font=ctk.CTkFont(size=13, weight="bold"))
        self.back_btn.pack(side="left", padx=30, pady=20)

        self.title_label = ctk.CTkLabel(self.header, text="🩺 DIABETES HEALTH ASSISTANT", 
                                        font=ctk.CTkFont(family="Inter", size=20, weight="bold"), 
                                        text_color="white")
        self.title_label.pack(side="right", padx=50, pady=20)

        # Chat History Area
        self.chat_display = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.chat_display.grid(row=1, column=0, sticky="nsew", padx=40, pady=(20, 10))
        
        # Quick Questions
        self.quick_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.quick_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=(0, 5))
        
        quick_qs = ["What is Diabetes?", "Symptoms", "Diet Tips", "Type 1 vs Type 2", "Normal Sugar Level"]
        for q in quick_qs:
            btn = ctk.CTkButton(self.quick_frame, text=q, height=30, width=130,
                                fg_color=COLOR_BORDER, hover_color=COLOR_TEXT_LIGHT,
                                text_color=COLOR_TEXT_DEEP, corner_radius=15,
                                font=ctk.CTkFont(size=11),
                                command=lambda question=q: self.quick_ask(question))
            btn.pack(side="left", padx=4, pady=5)

        # Input Area
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=3, column=0, sticky="ew", padx=40, pady=(0, 30))
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.user_input = ctk.CTkEntry(self.input_frame, placeholder_text="Ask about diabetes (e.g., symptoms, diet, types)...", 
                                       height=50, font=ctk.CTkFont(size=14),
                                       border_color=COLOR_BORDER, fg_color="white", text_color=COLOR_TEXT_DEEP)
        self.user_input.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.user_input.bind("<Return>", lambda e: self.send_message())

        self.send_btn = ctk.CTkButton(self.input_frame, text="SEND", width=100, height=50, 
                                      fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
                                      command=self.send_message, font=ctk.CTkFont(size=14, weight="bold"))
        self.send_btn.grid(row=0, column=1)

        # Initial Welcome Message
        self.add_message("Bot", "Hello! 👋 I'm your Diabetes Health Assistant.\n\n"
                         "I can answer questions about diabetes types, symptoms, diet, exercise, "
                         "blood sugar levels, prevention, and more.\n\n"
                         "Try the quick buttons below or type your question!")

    def add_message(self, sender, text):
        is_user = sender == "User"
        bg_color = COLOR_PRIMARY if is_user else COLOR_BG_CARD
        text_color = "white" if is_user else COLOR_TEXT_DEEP
        padx = (100, 10) if is_user else (10, 100)

        bubble_frame = ctk.CTkFrame(self.chat_display, fg_color="transparent")
        bubble_frame.pack(fill="x", pady=5)
        
        # Sender label
        if not is_user:
            sender_label = ctk.CTkLabel(bubble_frame, text="🤖 Assistant", 
                                        font=ctk.CTkFont(size=11, weight="bold"),
                                        text_color=COLOR_TEXT_MID)
            sender_label.pack(anchor="w", padx=12, pady=(2, 0))
        else:
            sender_label = ctk.CTkLabel(bubble_frame, text="You", 
                                        font=ctk.CTkFont(size=11, weight="bold"),
                                        text_color="white" if is_user else COLOR_TEXT_MID)
            sender_label.pack(anchor="e", padx=12, pady=(2, 0))

        bubble = ctk.CTkFrame(bubble_frame, fg_color=bg_color, corner_radius=15, 
                              border_width=1 if not is_user else 0, border_color=COLOR_BORDER)
        bubble.pack(side="right" if is_user else "left", padx=padx, pady=2)

        msg_label = ctk.CTkLabel(bubble, text=text, text_color=text_color, font=ctk.CTkFont(size=14), 
                                 wraplength=500, justify="left")
        msg_label.pack(padx=15, pady=10)
        
        # Scroll to bottom
        self.chat_display._parent_canvas.yview_moveto(1.0)

    def quick_ask(self, question):
        """Handle quick question button clicks."""
        self.user_input.delete(0, 'end')
        self.user_input.insert(0, question)
        self.send_message()

    def send_message(self):
        text = self.user_input.get().strip()
        if not text:
            return

        self.add_message("User", text)
        self.user_input.delete(0, 'end')
        
        # Get answer from offline knowledge base
        answer = find_best_answer(text)
        self.after(300, lambda: self.add_message("Bot", answer))  # Small delay for natural feel
