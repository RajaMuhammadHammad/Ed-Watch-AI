from flask import Flask, render_template, request, make_response, session
from rag_engine import retrieve_context
from xhtml2pdf import pisa
from io import BytesIO
from dotenv import load_dotenv
from datetime import datetime
import google.generativeai as genai
import os
import json
import re
import fitz 
import requests
 # PyMuPDF

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret")      
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))    
model = genai.GenerativeModel('gemini-2.0-flash')

@app.route("/", methods=["GET"])
@app.route("/home", methods=["GET"])
def home():  
    return render_template("index.html")

@app.route("/chatbot", methods=["GET"])
def chatbot():
    return render_template("chatbot.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = json.loads(request.form["chat_data"])

    # ✅ If report already exists in session, return cached version
    if session.get("report_html"):
        return render_template(
            "chatbot.html",
            response=session["report_html"],
            company_name=session.get("company_name", ""),
            region=session.get("region", ""),
            major_countries=session.get("major_countries", ""),
            sector_industry=session.get("sector_industry", ""),
            company_size=session.get("company_size", ""),
            listing_status=session.get("listing_status", ""),
            total_emissions=session.get("total_emissions", "")
        )
    
    query = f"Sustainability roadmap for a {data.get('company_size', '')} company in the {data.get('sector_industry', '')} sector located in {data.get('region', '')}, with focus on climate impact, energy consumption, emissions, and sustainability goals."
    retrieved_docs = retrieve_context(query)
    rag_context = "\n\n".join([doc.get("content", "") for doc in retrieved_docs])

    prompt = f"""
AI Persona & Role Definition
You are a top-tier sustainability and ESG (Environmental, Social, and Governance) consultant with 30 years of global experience. Your clientele includes multinational corporations across sectors like manufacturing, technology, and consumer goods. You are an expert in key reporting frameworks including the Global Reporting Initiative (GRI), Sustainability Accounting Standards Board (SASB), and the Task Force on Climate-related Financial Disclosures (TCFD), and you have deep knowledge of emerging regulations like the EU's Corporate Sustainability Reporting Directive (CSRD).
Your signature approach is to move beyond mere data reporting. You perform a strategic gap analysis, benchmarking a company's current state against industry best practices, regulatory expectations, and market leadership standards to produce a clear, actionable roadmap.
Core Task & Objective
Your primary task is to analyze the provided company sustainability data and generate a comprehensive, board-ready sustainability report in a single HTML file. The report must not only present the data but also provide expert observations and strategic recommendations for each section. The final output will serve as both a current-state assessment and a forward-looking strategic plan, including a detailed 5-year roadmap and specific KPIs.
[CONTEXT FROM KNOWLEDGE BASE / RAG RESULTS]
The following documents have been retrieved from the knowledge base to provide industry benchmarks, regulations, and best practices. Use this information strictly as reference material when analyzing and creating the report:
{rag_context}
[USER INPUT REQUIRED] - Company Profile & Diagnostic Data
1. Company Context (for more targeted analysis):
•    Company Name: [Insert Company Name]
•    Industry / Sector: [e.g., Apparel, Enterprise Software, Automotive Manufacturing]
•    Primary Geographic Operations: [e.g., North America, Southeast Asia, European Union]
•    Brief Business Model Description: [e.g., "Designs and sells consumer electronics through a global retail network with manufacturing outsourced to partners in Asia."]
2. Diagnostic Data Points:
(The AI will analyze the following data points to construct the report)
•    Strategy & Governance:
o    sustainability_strategy: "{data.get('sustainability_strategy', 'N/A')}"
o    governance_accountability: "{data.get('governance_accountability', 'N/A')}"
o    materiality_assessment: "{data.get('materiality_assessment', 'N/A')}"
o    erm_esg: "{data.get('erm_esg', 'N/A')}"
o    incentives_performance: "{data.get('incentives_performance', 'N/A')}"
o    framework_alignment: "{data.get('framework_alignment', 'N/A')}"
•    Policy & Compliance:
o    policies_monitoring: "{data.get('policies_monitoring', 'N/A')}"
•    Climate (Focus Area):
o    netzero_targets: "{data.get('netzero_targets', 'N/A')}"
o    scope_coverage: "{data.get('scope_coverage', 'N/A')}"
o    climate_disclosure: "{data.get('climate_disclosure', 'N/A')}"
o    decarbonization_plan: "{data.get('decarbonization_plan', 'N/A')}"
o    carbon_pricing: "{data.get('carbon_pricing', 'N/A')}"
o    transition_plan: "{data.get('transition_plan', 'N/A')}"
•    Energy, Resources & Circularity:
o    energy_management: "{data.get('energy_management', 'N/A')}"
o    renewables_adoption: "{data.get('renewables_adoption', 'N/A')}"
o    electrification_energy: "{data.get('electrification_energy', 'N/A')}"
o    waste_management: "{data.get('waste_management', 'N/A')}"
o    waste_diverted: "{data.get('waste_diverted', 'N/A')}"
o    product_sustainability: "{data.get('product_sustainability', 'N/A')}"
o    biodiversity_nature: "{data.get('biodiversity_nature', 'N/A')}"
o    green_buildings: "{data.get('green_buildings', 'N/A')}"
•    Water Stewardship:
o    water_measurement: "{data.get('water_measurement', 'N/A')}"
o    nature_based_solutions: "{', '.join(data.get('nature_based_solutions', [])) or 'None'}"
o    water_risk: "{data.get('water_risk', 'N/A')}"
o    water_efficiency: "{data.get('water_efficiency', 'N/A')}"
•    Supply Chain & Procurement:
o    supplier_esg: "{data.get('supplier_esg', 'N/A')}"
o    purchased_goods: "{data.get('purchased_goods', 'N/A')}"
o    sustainable_procurement: "{data.get('sustainable_procurement', 'N/A')}"
•    People, Culture & Training:
o    esg_training: "{data.get('esg_training', 'N/A')}"
o    staff_green: "{data.get('staff_green', 'N/A')}"
•    Data, Systems & Reporting:
o    data_systems: "{data.get('data_systems', 'N/A')}"
o    reporting_quality: "{data.get('reporting_quality', 'N/A')}"
•    External Signals:
o    ratings_certifications: "{data.get('ratings_certifications', 'N/A')}"
o    green_finance: "{data.get('green_finance', 'N/A')}"
Detailed Instructions for Report Generation
1. Analytical Approach (Apply this to every section):
For each topic (e.g., Governance, Climate, Water), you must follow a three-part structure:
•    Current Status (Observation): Synthesize the relevant input data points into a clear narrative. State what the company is currently doing or where information is lacking.
•    Expert Analysis & Gap Identification: Analyze the current status. Benchmark it against what leading companies in the industry are doing and what frameworks like TCFD or CSRD require. Clearly state the strategic gaps, risks, or missed opportunities. For example, if materiality_assessment is 'N/A', state: "The absence of a formal materiality assessment exposes the company to risks of focusing on non-critical ESG issues and failing to meet stakeholder expectations and upcoming regulatory requirements for disclosure."
•    Actionable Recommendations: Provide specific, concrete recommendations to close the identified gaps. Recommendations should be practical and prioritize actions that have the highest impact.
2. Report Structure and Content Mapping:
Generate the report using the exact section and subsection numbering and titles provided below. Use the input data as the basis for your analysis in the corresponding sections.
3. Roadmap and KPI Specificity:
•    The Five-Year Roadmap must be a direct consequence of the recommendations made throughout the report. Each year's initiatives should logically build upon the previous one.
•    The KPIs & Targets section must propose specific, measurable, achievable, relevant, and time-bound (SMART) goals. Instead of a generic "Reduce Waste," propose a target like "Reduce non-hazardous waste to landfill by 25% from a 2025 baseline by 2028."
4. HTML Formatting & Style:
•    Strictly adhere to the specified HTML structure: <h2> for main section headings, <h3> for subheadings, and <p>, <ul>, <li>, <div> for content.
•    Do NOT add a main title like "Sustainability Report," as this is handled by the application.
•    Ensure readability and professional presentation. Use inline CSS to style tables, lists, and headers for a clean, modern look. The final document must be well-organized and easily convertible to a PDF. Use a professional font-family like 'Inter', 'Helvetica', or 'Arial'.
•    Every <h2> section heading must start on a new page when converted to PDF. Apply inline style: <h2 style="page-break-before: always;"> except for the very first <h2>.
4. HTML Formatting & Style:
• Strictly adhere to the specified HTML structure: <h2> for main section headings, <h3> for subheadings, and <p>, <ul>, <li>, <div> for content.
• Do NOT add a main title like "Sustainability Report," as this is handled by the application.
• Ensure readability and professional presentation. Use inline CSS to style tables, lists, and headers for a clean, modern look. The final document must be well-organized and easily convertible to a PDF. Use a professional font-family like 'Inter', 'Helvetica', or 'Arial'.
• Every <h2> section heading must start on a new page when converted to PDF. Apply inline style: <h2 style="page-break-before: always;"> except for the very first <h2>.
• For tables: wrap them in <div style="page-break-inside: avoid;"> and use <table style="page-break-inside: avoid; width:100%; border-collapse: collapse;"> to ensure they fit on a single page without breaking.

[AI OUTPUT REQUIRED] - HTML Report Structure
IMPORTANT: Always generate all 14 sections in sequence, numbered exactly from 1 to 14. 
Do not skip or stop early, even if input data is missing. 
If data is missing, write "Data not available" but still generate the full section.
(Begin generating the HTML from this point forward, following all instructions above)
1. Company Profile
(Use the following data points to build the profile in a structured format with bullet points or a table.)
• Company Name: "{data.get('company_name', 'N/A')}"
• Region: "{data.get('region', 'N/A')}"
• Countries of Operation: "{data.get('major_countries', 'N/A')}"
• Sector & Industry: "{data.get('sector_industry', 'N/A')}"
• Company Size: "{data.get('company_size', 'N/A')}"
• Listing Status: "{data.get('listing_status', 'N/A')}"
• Total GHG Emissions: "{data.get('total_emissions', 'N/A')}"
• Date of Report: "{datetime.today().strftime('%B %d, %Y')}"
At the bottom of this section, always include the following disclaimer in italic style:
"This report is generated automatically using AI and provided data. Please review and verify the accuracy of the content before publishing or making business decisions."

2. Maturity Level
Use the score values to describe the maturity level of the company.
- Total Score: "{data.get('score_total', 'N/A')}"
- Level: "{data.get('score_level', 'N/A')}"
- Level Name: "{data.get('score_level_name', 'N/A')}"
- Confidence: "{data.get('confidence', 'N/A')}"
Explain what this maturity level means for the company in terms of sustainability journey.

3. Executive Summary
a. Purpose of the Report
(State the report's goal: to provide a comprehensive assessment of the company's current ESG maturity and a strategic roadmap for improvement.)
b. Findings based on AI diagnostic
(Summarize the most critical findings from your analysis, highlighting 3-4 key strengths and 3-4 major areas for development.)
c. Recommendations
(List the top 3-5 most impactful, high-priority recommendations that will drive the sustainability strategy forward.)

4. Governance & Strategy
(Analyze data points: sustainability_strategy, governance_accountability, materiality_assessment, erm_esg, incentives_performance, framework_alignment, policies_monitoring.)

5. Climate Strategy & Transition Plan
a. Greenhouse Gas (GHG) Inventory
(Analyze scope_coverage.)
b. Targets & SBTi Pathway
(Analyze netzero_targets.)
c. Decarbonization Levers & Capex Plan
(Analyze decarbonization_plan and carbon_pricing.)
d. Climate Risk & Resilience
(Analyze transition_plan.)
e. Disclosure
(Analyze climate_disclosure.)

6. Energy, Resources & Circularity
a. Energy management
(Analyze energy_management.)
b. Renewables
(Analyze renewables_adoption.)
c. Electrification & decentralized energy
(Analyze electrification_energy.)
d. Waste
(Analyze waste_management and waste_diverted.)
e. Product/service sustainability
(Analyze product_sustainability.)
f. Biodiversity & nature
(Analyze biodiversity_nature.)
g. Green buildings
(Analyze green_buildings.)

7. Water Stewardship
a. Measurement
(Analyze water_measurement.)
b. Basin stress mapping
(Analyze water_risk.)
c. Efficiency & reuse
(Analyze water_efficiency.)
d. Nature-based solutions
(Analyze nature_based_solutions.)

8. Supply Chain & Procurement
a. Supplier ESG expectations
(Analyze supplier_esg.)
b. Scope 3 - purchased goods/services
(Analyze purchased_goods.)
c. Sustainable procurement
(Analyze sustainable_procurement.)

9. People, Culture & Training
a. Training curriculum
(Analyze esg_training.)
b. Employee engagement
(Analyze staff_green.)
c. DEI & community
(Expand on the importance of social metrics, even if not explicitly in the data, as a key part of a holistic strategy.)

10. Data, Systems & Reporting
a. Systems
(Analyze data_systems.)
b. Controls
(Recommend data verification and assurance processes.)
c. Reporting
(Analyze reporting_quality and framework_alignment.)

11. External Signals & Green Finance
a. Ratings/certifications
(Analyze ratings_certifications.)
b. Green finance readiness
(Analyze green_finance.)

12. Five-Year Roadmap (2026-2030)
(Create a table or structured list for the roadmap, ensuring each year's initiatives are derived from your recommendations.)
a. 2026 — Planning & Foundation
b. 2027 — Measurement & Reduction
c. 2028 — Circularity & Engagement
d. 2029 — Certification & Reporting
e. 2030 — Science-Based Targets & Innovation

13. KPIs & Targets
(Propose specific, SMART targets in a table format for each category.)
a. GHG: S1+S2
b. Energy
c. Water
d. Waste
e. People
f. Supply chain
g. Data/assurance

14. Dependencies, Risks & Mitigations
(Outline potential challenges to implementing the roadmap in a   structured list.)
a. Data availability
b. Budget/capex
c. Change management

IMPORTANT: Always generate all 14 sections in sequence, numbered exactly from 1 to 14. 
Do not skip or stop early, even if input data is missing. 
If data is missing, write "Data not available" but still generate the full section.

"""

    response = model.generate_content(prompt, request_options={"timeout": 180})
    cleaned_html = re.sub(r"```(?:html)?\s*", "", response.text, flags=re.IGNORECASE)
    cleaned_html = re.sub(r"```", "", cleaned_html).strip()


   # ✅ Save report + user data into session
    session["report_html"] = cleaned_html
    session["company_name"] = data.get("company_name", "")
    session["region"] = data.get("region", "")
    session["major_countries"] = data.get("major_countries", "")
    session["sector_industry"] = data.get("sector_industry", "")
    session["company_size"] = data.get("company_size", "")
    session["listing_status"] = data.get("listing_status", "")
    session["total_emissions"] = data.get("total_emissions", "")

    return render_template("chatbot.html",
        response=cleaned_html,
        company_name=data.get('company_name', ''),
        region=data.get('region', ''),
        major_countries=data.get('major_countries', ''),
        sector_industry=data.get('sector_industry', ''),
        company_size=data.get('company_size', ''),
        listing_status=data.get('listing_status', ''),
        total_emissions=data.get('total_emissions','')
    )

@app.route("/download", methods=["POST"])
def download_pdf():
    html_content = request.form.get("response", "")
    company_name = request.form.get("company_name", "Company")


    html_content = re.sub(r"<h[1-7][^>]*>\s*.*?Sustainability Report.*?\s*</h[1-7]>", "", html_content, flags=re.IGNORECASE)
    html_content = re.sub(r"^\s*<div class='page-break'></div>", "", html_content, flags=re.IGNORECASE)

    # ✅ Section titles updated (now include maturity as first)
        # ✅ Section titles updated (now include maturity as first)
    section_titles = [
        "Company Profile",
        "Maturity Categorization (Diagnostic scoring model)",
        "Executive Summary",
        "Governance & Strategy",
        "Climate Strategy & Transition Plan",
        "Energy, Resources & Circularity",
        "Water Stewardship",
        "Supply Chain & Procurement",
        "People, Culture & Training",
        "Data, Systems & Reporting",
        "External Signals & Green Finance",
        "Five-Year Roadmap (2026–2030)",
        "KPIs & Targets",
        "Dependencies, Risks & Mitigations"
    ]

    
    for i, title in enumerate(section_titles, start=1):
          pattern = rf"<h2[^>]*>\s*{i}\.\s*{re.escape(title)}\s*</h2>"
          replacement = (
        f"<h2 style='page-break-before: always; "
        f"color:#000000; font-family:Calibri, Arial, sans-serif; "
        f"font-size:20pt; font-weight:bold; margin-top:40px; margin-bottom:15px;'>"
        f"{i}. {title}</h2>"
    )
    html_content = re.sub(pattern, replacement, html_content, flags=re.IGNORECASE)


    full_html = f"""
    <html>
    <head>
    <style>
        @page {{ margin: 1in; }}
        body {{
            font-family: Arial, sans-serif;
            font-size: 12pt;
            line-height: 1.4;
            color: #000;
        }}
        .company-info {{ text-align: center; margin-top: 80px; }}
        .page-break {{ page-break-before: always; }}
        h2 {{
                color: #000000 !important;   /* force black */
                font-family: Calibri;
                font-size: 24pt;   /* bigger size */
                margin-top: 40px;
                margin-bottom: 15px;
         }}
        h3 {{
            color: #000000 !important;
            font-size: 14pt;
            margin-top: 15px;
            margin-bottom: 10px;
            border-bottom: 1px solid #ccc;
            padding-bottom: 4px;
        }}
        .section-box {{
            background-color: #f4f9ff;
            border: 1px solid #cfdff4;
            border-top: none;
            border-radius: 0 0 8px 8px;
            padding: 15px 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 30px;
        }}
        p {{ margin: 4px 0 6px 0; text-align: justify; }}
        ul {{ margin-left: 20px; }}
        li {{ margin-bottom: 6px; }}
    </style>
    </head>
    <body>


        <div class="report-body">
            {html_content}
        </div>

    </body>
    </html>
    """

    report_pdf_stream = BytesIO()
    pisa_status = pisa.CreatePDF(full_html, dest=report_pdf_stream)
    if pisa_status.err:
        return "PDF generation failed", 500
    report_pdf_stream.seek(0)

    blank_template_path = "static/Template.pdf"
    if not os.path.exists(blank_template_path):
        return "Template not found", 404
    template_doc = fitz.open(blank_template_path)
    content_doc = fitz.open("pdf", report_pdf_stream.getvalue())
    
    final_pdf = fitz.open()

    cover_path = "static/cover.pdf"
    if os.path.exists(cover_path):
        cover_doc = fitz.open(cover_path)   
        final_pdf.insert_pdf(cover_doc)


    for i, page in enumerate(content_doc):
        bg_page = template_doc[0]
        new_page = final_pdf.new_page(width=bg_page.rect.width, height=bg_page.rect.height)
        new_page.show_pdf_page(bg_page.rect, template_doc, 0)
        new_page.show_pdf_page(bg_page.rect, content_doc, i)

    appendix_path = "static/Details.pdf"
    if os.path.exists(appendix_path):
        appendix = fitz.open(appendix_path)
        final_pdf.insert_pdf(appendix)

    output = BytesIO()
    final_pdf.save(output)
    output.seek(0)
    pdf_bytes = output.getvalue()

    response = make_response(pdf_bytes)
    response.headers["Content-Disposition"] = f"attachment; filename={company_name}_sustainability_report.pdf"
    response.headers["Content-Type"] = "application/pdf"
    return response



@app.route("/validate-email", methods=["POST"])
def validate_email():
    email = request.json.get("email")
    if not email:
        return {"valid": False, "error": "Email is required"}, 400

    api_key = os.getenv("ABSTRACT_API_KEY")
    if not api_key:
        return {"valid": False, "error": "API key missing"}, 500

    url = f"https://emailreputation.abstractapi.com/v1/?api_key={api_key}&email={email}"

    try:
        response = requests.get(url)
        result = response.json()

        # ✅ Adjusted for new response format
        deliverability = result.get("email_deliverability", {}).get("status")
        is_format_valid = result.get("email_deliverability", {}).get("is_format_valid", False)

        is_valid = (
            is_format_valid and deliverability in ["deliverable", "risky"]
        )

        return {"valid": is_valid, "raw": result}
    except Exception as e:
        print("Email validation error:", e)
        return {"valid": False, "error": "Validation failed"}, 500


    except Exception as e:
        print("Email validation error:", e)
        return {"valid": False, "error": "Validation failed"}, 500


if __name__ == "__main__":
    app.run(debug=True)


