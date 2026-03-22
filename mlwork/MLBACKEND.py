from flask import Flask, render_template, request #request frontend se cheeze uthane ke liye kaam aata hai
# import google.generativeai as genai # gemini ki api key lene ke liye 
'''iski jagah me groq use karunga woh free hai '''
from groq import Groq
import os # apne os prr kaam krnr ke liye
import PyPDF2 #pdf read ke liye

# APP
app = Flask(__name__)

# API Key
#enai.configure(api_key="AIzaSyAafkKNuRZHg2d5owMxkx_7b9T96IK1t2I")
client = Groq(api_key="gsk_xxxxxxxxxxxxxxxxxxxxxxxx")

# Initialize model
# model = genai.GenerativeModel("gemini-2.0-flash")

def predict_fake_or_real(text):
    prompt = f"""
        You are an expert in detecting fraud, scams, and fake government schemes.

        Analyze the following content carefully and determine whether it is:
        1. REAL / LEGITIMATE
        2. FAKE / SCAM

        Content:
        {text}

        Instructions:
        - Always return a result (never return empty or null).
        - Clearly state one of the two labels: REAL or FAKE.
        - Give a short but clear explanation (2-4 lines).
        - If suspicious elements exist (like urgency, free money, unknown links), mention them.
        - If it looks official, explain why it seems trustworthy.

        Output format:
        Result: REAL or FAKE  
        Reason: <clear explanation>
        """

    try:
        response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}])
        return response.choices[0].message.content
    except Exception as e:
        return f"Error during analysis: {str(e)}"

def url_detection(url):
    prompt = f"""
        You are a senior cybersecurity analyst working with the Indian Government's 
        cyber crime department. You specialize in detecting FAKE GOVERNMENT SCHEME URLs 
        that fraud citizens by impersonating official government portals.

        Analyze this URL: {url}

        ═══════════════════════════════════════════
        MAJOR FACTORS TO CHECK (in order of priority):
        ═══════════════════════════════════════════

        1. DOMAIN AUTHENTICITY (Most Important)
           - Real Indian govt URLs ALWAYS end with: .gov.in / .nic.in / .india.gov.in
           - Real state govt URLs: [state].gov.in (e.g., up.gov.in, mp.gov.in)
           - Fake sites use: .com, .org, .in, .xyz, .net pretending to be govt
           - Example REAL: pmay.gov.in, pmkisan.gov.in, digitalindia.gov.in
           - Example FAKE: pmay-yojana.com, pm-kisan-help.in, digital-india-scheme.org

        2. HTTPS vs HTTP CHECK (Very Important)
           - HTTPS = encrypted and secure connection ✅
           - HTTP = unencrypted, insecure connection ❌
           - Even if the domain is .gov.in, HTTP means MEDIUM risk minimum
           - All real official Indian govt portals use HTTPS
           - http://pmjay.gov.in = MEDIUM risk (correct domain, wrong protocol)
           - http://anythingelse.com = HIGH risk (wrong domain + wrong protocol)

        3. SCHEME NAME MANIPULATION
           - Check if popular scheme names are used to trick users:
             * PM Awas Yojana / PMAY
             * PM Kisan Samman Nidhi
             * Ayushman Bharat / PMJAY
             * Ujjwala Yojana
             * Jan Dhan Yojana
             * Mudra Loan Yojana
             * Sukanya Samriddhi
             * Atal Pension Yojana
             * Free Laptop / Tablet schemes
             * Ration Card schemes
             * Scholarship schemes
           - Fraudsters add words like: "apply", "registration", "helpline", 
             "form", "status", "check", "free", "yojana", "sarkari" to fake URLs

        4. PHISHING KEYWORDS IN URL
           - Extremely suspicious if URL contains:
             * "free-money", "cash-transfer", "instant-loan"
             * "apply-now", "last-date", "urgent", "limited"
             * "kyc-update", "aadhar-link", "pan-verify"
             * "helpline", "customer-care", "toll-free"
             * "win", "prize", "lucky", "selected", "congratulations"
             * "form-fill", "registration-open", "benefit-claim"

        5. URL STRUCTURE RED FLAGS
           - Too many hyphens: pm-kisan-yojana-apply-now-free.com ❌
           - Govt name as subdomain of fake domain: gov.india-scheme.com ❌
           - Numbers replacing letters: 1ndia-scheme.com, g0v-portal.in ❌
           - Extra words added: pmkisan-official-portal.com ❌
           - IP address instead of domain: http://192.168.1.1/pmay ❌

        6. IMPERSONATION PATTERNS
           - Adding "official", "sarkari", "govt" to non-govt domains
           - Cloning real scheme names with slight changes
           - Using state names to seem local and trustworthy
           - Adding "2024" or "2025" to seem updated and current

        7. FINANCIAL FRAUD INDICATORS
           - URLs promising: free money, loan without documents,
             guaranteed approval, subsidy claim, direct bank transfer
           - These are ALWAYS fake - real govt sites never promise this in URL

        ═══════════════════════════════════════════
        OUTPUT FORMAT (strictly follow this):
        ═══════════════════════════════════════════

        Result: REAL ✅ or FAKE ❌ or SUSPICIOUS ⚠️

        Risk Level: 🟢 LOW or 🟡 MEDIUM or 🔴 HIGH

        Scheme Targeted: <which govt scheme is being impersonated, if any>

        Domain Check: <is domain .gov.in/.nic.in or fake domain?>

        Protocol Check: <is it HTTPS or HTTP? mention if insecure>

        Reason:
        - <point 1>
        - <point 2>
        - <point 3>

        Red Flags Found:
        - <flag 1>
        - <flag 2>
        - <flag 3 if any>

        Citizen Advisory: <1 line advice for common citizens in simple language>

        ═══════════════════════════════════════════
        EXAMPLES:
        ═══════════════════════════════════════════

        Example 1 - FAKE:
        URL: http://pm-kisan-yojana-apply-free-money.com/registration

        Result: FAKE ❌
        Risk Level: 🔴 HIGH
        Scheme Targeted: PM Kisan Samman Nidhi
        Domain Check: Uses .com instead of official pmkisan.gov.in
        Protocol Check: HTTP — insecure and unencrypted connection
        Reason:
        - Domain is not a .gov.in domain
        - Contains phishing keywords like "apply", "free", "money"
        - Multiple hyphens indicate a fake constructed URL
        Red Flags Found:
        - Not a .gov.in domain
        - Contains "free-money" — government never uses this in URLs
        - HTTP not HTTPS
        Citizen Advisory: Kabhi bhi .gov.in ke alawa kisi site par apni bank ya Aadhar details mat dena!

        Example 2 - REAL:
        URL: https://pmkisan.gov.in/

        Result: REAL ✅
        Risk Level: 🟢 LOW
        Scheme Targeted: PM Kisan Samman Nidhi (Official)
        Domain Check: Official .gov.in domain confirmed
        Protocol Check: HTTPS — secure and encrypted connection ✅
        Reason:
        - Verified official government portal for PM Kisan Samman Nidhi
        - Hosted on trusted .gov.in domain managed by NIC
        - Uses secure HTTPS protocol
        Red Flags Found: None
        Citizen Advisory: Yeh official government website hai, safe hai.

        Example 3 - SUSPICIOUS:
        URL: http://pmjay.gov.in

        Result: SUSPICIOUS ⚠️
        Risk Level: 🟡 MEDIUM
        Scheme Targeted: Ayushman Bharat / PMJAY
        Domain Check: Domain is correct .gov.in but protocol is insecure
        Protocol Check: HTTP — connection is NOT encrypted, data can be intercepted
        Reason:
        - Domain pmjay.gov.in is the correct official domain
        - However HTTP is used instead of HTTPS which is insecure
        - Real official govt portals always use HTTPS, never HTTP
        Red Flags Found:
        - HTTP instead of HTTPS — your data is not safe on this connection
        - Official site should always be https://pmjay.gov.in
        Citizen Advisory: Sahi domain hai par HTTP unsafe hai — hamesha https:// wala link use karo!

        ═══════════════════════════════════════════
        Now analyze the given URL strictly in the above format.
        Every field must be on its own line. Never write in paragraph form.
        Be strict — HTTP on any site including .gov.in = minimum MEDIUM risk.
        ═══════════════════════════════════════════
        """
    
    
    try:
        response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}])
        return response.choices[0].message.content
    except Exception as e:
        return f"Error during analysis: {str(e)}"


# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/scam/", methods=['GET', 'POST'])
def detect_scam():
    if 'file' not in request.files:
        return render_template("index.html", message="No file uploaded.")

    file = request.files['file']

    if file.filename == "":
        return render_template("index.html", message="No file selected.")

    extracted_text = ""

    try:
        if file.filename.endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(file)
            extracted_text = "".join([
                page.extract_text() for page in pdf_reader.pages if page.extract_text()
            ])

        elif file.filename.endswith(".txt"):
            extracted_text = file.read().decode("UTF-8")

        else:
            return render_template("index.html", message="❌ Only .pdf or .txt files are supported!")

        if not extracted_text.strip():
            return render_template("index.html", message="⚠️ File is empty or text could not be extracted.")

        message = predict_fake_or_real(extracted_text)

    except Exception as e:
        message = f"Error processing file: {str(e)}"

    return render_template("index.html", message=message)
@app.route("/predict",methods=['GET','POST'])
@app.route("/predict", methods=['GET', 'POST'])
def url_predict():
    if request.method == 'POST':
        url = request.form.get("url", "").strip()

        if not url.startswith(('http://', 'https://')):
            return render_template("index.html", message="Invalid URL format bhaiya...")

        classification = url_detection(url)
        return render_template("index.html", input_url=url, predicted_class=classification)

    # ADD THIS — handle GET request
    return render_template("index.html")




# MAIN
if __name__ == "__main__":
    app.run(debug=True)