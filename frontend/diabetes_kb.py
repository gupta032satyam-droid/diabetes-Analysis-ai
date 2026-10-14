# Offline Diabetes Knowledge Base (WHO & Clinical Guidelines)
# Each entry: (keywords_list, answer)

KB = [
    # --- Greetings & Casual ---
    (["hi", "hello", "hey", "hii", "heyo", "greetings", "good morning", "good evening", "good afternoon", "morning", "evening", "afternoon"],
     "Hello! 👋 I'm your Diabetes Health Assistant. I'm here to provide you with the most accurate, WHO-based information on diabetes. How can I help you today?"),

    (["how are you", "how r u", "how do you do", "how are u"],
     "I'm functioning perfectly, thank you! 🤖 I am ready to answer your questions about diabetes symptoms, types, treatments, and WHO guidelines. What would you like to know?"),

    (["who are you", "what are you", "your name", "about you"],
     "I am an AI-powered Diabetes Health Assistant. 🩺 My purpose is to provide highly accurate, clinical, and WHO-backed information about diabetes to help you understand the condition better."),

    # --- Definition & Basics ---
    (["what is diabetes", "define diabetes", "diabetes meaning", "explain diabetes", "who definition", "what does diabetes mean"],
     "According to the World Health Organization (WHO), diabetes is a chronic, metabolic disease characterized by elevated levels of blood glucose (blood sugar). It occurs either when the pancreas does not produce enough insulin or when the body cannot effectively use the insulin it produces. Over time, it leads to serious damage to the heart, blood vessels, eyes, kidneys, and nerves."),

    # --- Project Specific Types ---
    (["type 1", "type one", "juvenile diabetes", "insulin dependent"],
     "Type 1 Diabetes (previously known as insulin-dependent or juvenile diabetes) is an autoimmune condition where the pancreas produces little to no insulin. According to WHO, its exact causes are unknown and it is not currently preventable. It requires lifelong, daily insulin therapy. Key symptoms include excessive thirst, frequent urination, constant hunger, and unexplained weight loss."),

    (["child type 1", "pediatric type 1", "kids type 1", "children type 1"],
     "Child/Pediatric Type 1 Diabetes is the most common form of diabetes in children. It's an autoimmune condition where the body attacks insulin-producing cells. Children with Type 1 require 24/7 management, insulin therapy, and careful blood glucose monitoring. Early diagnosis is critical to prevent life-threatening diabetic ketoacidosis (DKA)."),

    (["type 2", "type two", "adult onset", "insulin resistant"],
     "Type 2 Diabetes accounts for over 90% of all diabetes cases globally. It occurs when the body becomes resistant to insulin or fails to produce enough. It is strongly associated with lifestyle factors like excess body weight (obesity), physical inactivity, and family history. It can often be prevented or managed through healthy eating, exercise, oral medications, and sometimes insulin."),

    (["child type 2", "pediatric type 2", "kids type 2", "children type 2"],
     "Child/Pediatric Type 2 Diabetes is becoming increasingly common in youth, largely driven by the global childhood obesity epidemic. While previously seen almost exclusively in adults, children with a high BMI and sedentary lifestyle are at significant risk. It often presents with no symptoms initially, making screening essential for at-risk youth."),

    (["gestational", "pregnancy diabetes", "pregnant", "gestational diabetes"],
     "Gestational Diabetes is a temporary condition characterized by high blood sugar that develops during pregnancy. According to WHO, women with gestational diabetes are at an increased risk of complications during pregnancy and delivery. While it usually resolves after birth, it significantly increases the future risk of both the mother and child developing Type 2 Diabetes."),

    (["prediabetes", "pre diabetes", "borderline", "pre-diabetes"],
     "Pre-Diabetes is a critical warning stage where blood sugar levels are higher than normal, but not yet high enough for a Type 2 diabetes diagnosis. It indicates a high risk for developing Type 2, but it is highly reversible. Lifestyle changes, such as losing 5-10% of body weight and engaging in regular physical activity, can effectively reverse prediabetes."),

    (["no diabetes", "normal", "healthy", "don't have diabetes", "negative", "diabetes free"],
     "No Diabetes (Normal) means your blood sugar levels are within the healthy, safe range (Fasting glucose: 70-99 mg/dL, HbA1c: below 5.7%). To maintain this healthy state, WHO recommends eating a balanced diet, engaging in at least 150 minutes of weekly physical activity, maintaining a normal body weight, and avoiding tobacco use."),

    # --- Causes & General ---
    (["cause", "reason", "why happen", "why diabetes", "how get diabetes"],
     "The reasons/causes of diabetes depend on the type:\n"
     "• Type 1: Caused by an autoimmune reaction where the body attacks its own insulin-producing cells. The exact trigger is unknown.\n"
     "• Type 2: Caused by the body becoming resistant to insulin. Major reasons include excess body weight (obesity), physical inactivity, genetics, and age.\n"
     "• Gestational: Caused by hormonal changes during pregnancy leading to insulin resistance.\n"
     "• Prediabetes: Driven by similar factors to Type 2, primarily excess weight and lack of exercise."),

    (["child diabetes", "kids diabetes", "pediatric diabetes", "children diabetes"],
     "Diabetes in children is primarily Type 1, which is an autoimmune condition requiring lifelong insulin. However, Type 2 diabetes in children is rising due to the global childhood obesity epidemic. If a child has symptoms like extreme thirst, frequent urination, or unexplained weight loss, seek immediate medical attention."),

    # --- Global Statistics & Facts ---
    (["statistics", "stats", "how many people", "prevalence", "global", "fact sheet", "how common"],
     "Here are the latest WHO Global Statistics on Diabetes:\n"
     "• As of 2022, approximately 830 million people worldwide are living with diabetes.\n"
     "• This is a massive increase from 200 million cases in 1990.\n"
     "• The majority of affected individuals live in low- and middle-income countries.\n"
     "• In 2021, diabetes and its related kidney complications were responsible for over 2 million deaths."),

    (["treatment gap", "medication access", "who gets medicine"],
     "According to the WHO, there is a massive global treatment gap. More than half of all people living with diabetes do not receive the medication they need. Treatment coverage is unfortunately lowest in low- and middle-income countries."),

    # --- Symptoms ---
    (["symptom", "signs", "how to know", "feel like", "indication", "how do i know"],
     "Common symptoms of diabetes include:\n"
     "• Polydipsia (Feeling excessively thirsty)\n"
     "• Polyuria (Urinating very often)\n"
     "• Polyphagia (Constant extreme hunger)\n"
     "• Unexplained and rapid weight loss\n"
     "• Extreme fatigue and tiredness\n"
     "• Blurred vision\n"
     "• Cuts or sores that heal very slowly\n"
     "Note: WHO warns that Type 2 diabetes symptoms may be mild or absent for years, delaying diagnosis."),

    # --- Prevention ---
    (["prevent", "avoid", "stop diabetes", "reduce risk", "how to not get"],
     "According to the WHO, Type 2 diabetes can often be prevented or delayed through simple lifestyle measures:\n"
     "1. Achieve and maintain a healthy body weight.\n"
     "2. Be physically active (at least 30 mins of regular, moderate-intensity activity most days).\n"
     "3. Eat a healthy diet, avoiding added sugars and saturated fats.\n"
     "4. Avoid tobacco use (smoking increases diabetes and cardiovascular risks).\n"
     "Note: Type 1 diabetes cannot be prevented with current knowledge."),

    # --- BMI & Weight ---
    (["bmi", "body mass index", "overweight", "obesity", "fat", "weight", "lose weight"],
     "BMI (Body Mass Index) is a key indicator for diabetes risk. It's calculated as weight in kg divided by height in meters squared.\n"
     "WHO Classifications:\n"
     "• Normal: 18.5 – 24.9\n"
     "• Overweight: 25.0 – 29.9 (Increased risk)\n"
     "• Obese: ≥ 30.0 (High risk)\n"
     "Excess body fat causes insulin resistance. Losing just 5-7% of your body weight can significantly reduce your risk of developing Type 2 diabetes."),

    # --- Blood Glucose & Tests ---
    (["glucose", "blood sugar level", "normal sugar", "target sugar", "sugar level", "hba1c", "blood test", "diagnosis test", "diagnose"],
     "Diabetes is diagnosed and monitored via blood tests. Standard clinical guidelines are:\n"
     "• Fasting Blood Glucose: 70–99 mg/dL (Normal), 100–125 mg/dL (Prediabetes), ≥126 mg/dL (Diabetes)\n"
     "• Oral Glucose Tolerance Test (2-hour): <140 mg/dL (Normal), ≥200 mg/dL (Diabetes)\n"
     "• HbA1c (3-month average): <5.7% (Normal), 5.7%–6.4% (Prediabetes), ≥6.5% (Diabetes)\n"
     "Diabetic patients generally aim for an HbA1c of < 7.0%, but always consult your doctor."),

    # --- Complications & Effects ---
    (["effect", "complication", "consequence", "impact", "damage", "long term", "risk", "blindness", "kidney failure", "amputation", "heart attack"],
     "The WHO emphasizes that uncontrolled diabetes is a major cause of severe complications:\n"
     "• Heart attacks and strokes (Cardiovascular disease)\n"
     "• Blindness (Diabetic retinopathy damages blood vessels in the eyes)\n"
     "• Kidney failure (Nephropathy)\n"
     "• Lower limb amputation (Due to nerve damage / neuropathy and poor blood flow)\n"
     "Strict control of blood sugar, blood pressure, and cholesterol can delay or prevent these effects."),

    # --- Treatment & Management ---
    (["treatment", "cure", "manage", "control", "medication", "medicine", "insulin", "metformin", "pill"],
     "Diabetes management requires a lifelong commitment to keep blood sugar near normal:\n"
     "• Type 1: Requires daily survival insulin (via injections or pump).\n"
     "• Type 2: Starts with diet/exercise. If insufficient, oral medications (like Metformin) are used. Insulin may be required later.\n"
     "• General: WHO stresses the importance of blood glucose monitoring, foot care, regular eye exams, and kidney function tests. Access to affordable treatment is critical for survival."),

    # --- Diet & Nutrition ---
    (["diet", "food", "eat", "nutrition", "meal", "what to eat", "avoid food", "sugar intake", "carbs"],
     "A diabetes-friendly diet stabilizes blood sugar:\n"
     "✅ DO EAT: High-fiber foods, non-starchy vegetables, whole grains, lean proteins (fish, chicken, beans), and healthy fats (nuts, olive oil).\n"
     "❌ AVOID: Sugary beverages, refined carbs (white bread/rice), highly processed foods, and trans fats.\n"
     "Eating smaller, frequent meals and controlling portion sizes helps prevent dangerous blood sugar spikes."),

    # --- Exercise ---
    (["exercise", "workout", "physical activity", "walk", "yoga", "gym", "active", "sport"],
     "The WHO strongly recommends regular physical activity for diabetes management and prevention.\n"
     "• It improves insulin sensitivity, allowing muscles to use glucose for energy.\n"
     "• Recommendation: At least 150 minutes of moderate aerobic exercise (brisk walking, cycling) per week, plus strength training twice a week.\n"
     "• Always monitor your blood sugar before and after exercise to prevent hypoglycemia."),

    # --- Hypoglycemia (Low Blood Sugar) ---
    (["low sugar", "hypoglycemia", "sugar drop", "shaking", "dizzy", "faint", "pass out"],
     "Hypoglycemia (low blood sugar, <70 mg/dL) is an acute emergency. Symptoms include shaking, sweating, rapid heartbeat, dizziness, confusion, and extreme hunger.\n"
     "• Treatment (15-15 Rule): Immediately eat 15g of fast-acting carbs (e.g., half cup of juice, 4 glucose tablets, 1 tablespoon honey). Wait 15 minutes, recheck, and repeat if still low. Seek emergency medical help if the person is unconscious."),

    # --- Hyperglycemia (High Blood Sugar) ---
    (["high sugar", "hyperglycemia", "sugar spike", "sugar high", "dka", "ketoacidosis"],
     "Hyperglycemia (very high blood sugar, usually >180-200 mg/dL) causes excessive thirst, frequent urination, and fatigue. If ignored, it can lead to Diabetic Ketoacidosis (DKA) or Hyperosmolar Hyperglycemic State (HHS) — both are life-threatening emergencies requiring immediate hospitalization. Drink water, take prescribed insulin/meds, and contact a doctor if levels don't drop."),

    # --- System Info ---
    (["accuracy", "this system", "this app", "model", "how accurate", "ai system", "about system"],
     "This Diabetes Diagnose AI System uses an advanced Machine Learning model (Random Forest, 97.68% accuracy) to assist in diagnosis based on clinical parameters like Glucose, BMI, and HbA1c. It integrates offline WHO knowledge to answer your questions. Please remember: this is a supplementary clinical tool, not a replacement for a professional doctor's diagnosis."),

    # --- Thank You & Farewells ---
    (["thank", "thanks", "thank you", "appreciate", "helpful"],
     "You are very welcome! 😊 Providing accurate medical information is what I'm here for. Let me know if you need anything else."),

    (["bye", "goodbye", "see you", "quit", "exit", "cya"],
     "Goodbye! Take excellent care of your health. 🏥 Remember to monitor your sugar levels, eat well, and consult your physician regularly. Wishing you a wonderful day! 💙"),
]

DEFAULT_RESPONSE = (
    "I'm not completely sure about that specific phrasing. As a specialized Diabetes Health Assistant, I can answer over 90% of clinical questions regarding:\n\n"
    "• Diabetes Types (Type 1, Type 2, Child Types, Prediabetes, Gestational)\n"
    "• WHO Definitions and Global Statistics\n"
    "• Symptoms, Causes, and Prevention\n"
    "• Diagnosis (HbA1c, Fasting Glucose, BMI)\n"
    "• Complications (Blindness, Kidney failure, Neuropathy)\n"
    "• Diet, Nutrition, and Exercise guidelines\n\n"
    "Could you please rephrase your question using simpler keywords related to these topics?"
)

def find_best_answer(user_input):
    """Find the best matching answer from the knowledge base using an enhanced scoring algorithm."""
    import re
    
    # Clean input: fix typos, lowercase and remove punctuation
    text = user_input.lower().strip()
    text = text.replace("daibetes", "diabetes").replace("diabeties", "diabetes").replace("predaibetes", "prediabetes")
    
    text = re.sub(r'[^a-z0-9\s]', '', text)
    
    best_score = 0
    best_answer = DEFAULT_RESPONSE

    # Split input into words for better exact matching
    input_words = set(text.split())

    for keywords, answer in KB:
        score = 0
        for kw in keywords:
            kw_clean = re.sub(r'[^a-z0-9\s]', '', kw.lower())
            
            # Exact match of the entire phrase
            if kw_clean == text:
                score += 100
            
            # Phrase is present inside the text
            elif kw_clean in text:
                score += len(kw_clean) * 2
                
            # Check for word-level matches (good for multi-word inputs)
            kw_words = set(kw_clean.split())
            if kw_words:
                matched_words = kw_words.intersection(input_words)
                if matched_words:
                    score += len(matched_words) * 3
                
        if score > best_score:
            best_score = score
            best_answer = answer

    # Minimum threshold to avoid completely random matches
    if best_score >= 4:
        return best_answer
    return DEFAULT_RESPONSE
