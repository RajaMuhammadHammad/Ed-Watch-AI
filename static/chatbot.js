/* -------- Chat state -------- */
let step = 0;
let data = {};
let scores = {}; // field -> numeric score (0..3 except checkboxes)
let currentChatId = null; // reserved for future use

/* -------- Boot -------- */
document.addEventListener("DOMContentLoaded", () => {
  nextStep();
});

/* =========================================================
   FLOW
========================================================= */
function nextStep(inputValue) {
  if (inputValue !== undefined && inputValue !== null && inputValue !== "") {
    appendUserMessage(inputValue);
  }

  showTypingIndicator();

  setTimeout(() => {
    hideTypingIndicator();

    switch (step) {
      /* ======== Company Profile ======== */
      case 0:
        askInput("What's your company name?", "company_name", "fas fa-building");
        break;

      case 1:
        askButtons(
          "Which region best describes your primary market?",
          [
            { value: "North America" },
            { value: "Latin America" },
            { value: "Europe (Western)" },
            { value: "Europe (Eastern)" },
            { value: "Middle East (excl. KSA)" },
            { value: "KSA (Saudi Arabia)" },
            { value: "Africa (Sub-Saharan)" },
            { value: "Africa (North)" },
            { value: "Asia (East)" },
            { value: "Asia (South)" },
            { value: "Asia (Southeast)" },
            { value: "Central Asia" },
            { value: "Oceania" },
          ],
          "region",
          { score: false }
        );
        break;

      case 2:
        askInput("Which major countries do you operate in?", "major_countries", "fas fa-building");
        break;

      case 3:
        askInput(
          "Please specify your sector & industry (e.g., Renewable Energy, Pharmaceuticals, AgriTech)",
          "sector_industry"
        );
        break;

      case 4:
        askButtons(
          "What is your company size?",
          [
            { value: "0 - 100" },
            { value: "101 - 500" },
            { value: "501 - 1000" },
            { value: "1001 - 2000" },
            { value: "2001 & above" },
          ],
          "company_size",
          { score: false }
        );
        break;

      case 5:
        askButtons(
          "Is your company listed or unlisted?",
          [{ value: "Listed" }, { value: "Unlisted" }],
          "listing_status",
          { score: false }
        );
        break;

      case 6:
        askInput("What is your total annual GHG emissions (in tCO2e)?", "total_emissions");
        break;

      /* ======== Scored Maturity Questions (7..40) ======== */
      case 7:
        askButtons(
          "Documented sustainability strategy:",
          [{ value: "None" }, { value: "Draft" }, { value: "Approved & shared" }, { value: "Integrated with KPIs" }],
          "sustainability_strategy"
        );
        break;

      case 8:
        askButtons(
          "Governance & accountability:",
          [{ value: "None" }, { value: "Ad hoc owner" }, { value: "Committee + owner" }, { value: "Board/Exec oversight" }],
          "governance_accountability"
        );
        break;

      case 9:
        askButtons(
          "Materiality assessment:",
          [{ value: "None" }, { value: "Informal" }, { value: "Structured/periodic" }, { value: "Aligned & strategy-driven" }],
          "materiality_assessment"
        );
        break;

      case 10:
        askButtons(
          "ERM integration of ESG:",
          [{ value: "Not in ERM" }, { value: "Parallel list" }, { value: "In ERM" }, { value: "Scenario-tested in ERM" }],
          "erm_esg"
        );
        break;

      case 11:
        askButtons(
          "Incentives/performance links:",
          [{ value: "None" }, { value: "Informal" }, { value: "Exec KPIs" }, { value: "Cascaded KPIs" }],
          "incentives_performance"
        );
        break;

      case 12:
        askButtons(
          "Framework alignment maturity:",
          [{ value: "None" }, { value: "Awareness" }, { value: "Formal (≥1)" }, { value: "Multi-framework + updates" }],
          "framework_alignment"
        );
        break;

      case 13:
        askButtons(
          "Policies & monitoring:",
          [
            { value: "None" },
            { value: "Few/ad hoc" },
            { value: "Multi-policy + internal tracking" },
            { value: "Full E/S/G + audits" },
          ],
          "policies_monitoring"
        );
        break;

      case 14:
        askButtons(
          "Net-zero/targets:",
          [{ value: "None" }, { value: "Undisclosed aims" }, { value: "Target set (SBTi pending)" }, { value: "SBTi-validated + milestones" }],
          "netzero_targets"
        );
        break;

      case 15:
        askButtons(
          "Scope coverage:",
          [{ value: "None" }, { value: "Partial S1/2" }, { value: "Full S1-2" }, { value: "S1-2 + material S3" }],
          "scope_coverage"
        );
        break;

      case 16:
        askButtons(
          "Climate disclosure alignment:",
          [{ value: "None" }, { value: "Aware only" }, { value: "Partial (e.g., CDP/TCFD pilot)" }, { value: "Full (ISSB S2/TCFD/CDP)" }],
          "climate_disclosure"
        );
        break;

      case 17:
        askButtons(
          "Decarbonization levers in plan:",
          [{ value: "None" }, { value: "Energy efficiency" }, { value: "+ RE power" }, { value: "+ Value-chain (S3)" }],
          "decarbonization_plan"
        );
        break;

      case 18:
        askButtons(
          "Carbon pricing/use in decisions:",
          [{ value: "None" }, { value: "Shadow price explored" }, { value: "Shadow price applied" }, { value: "Internal price drives capex" }],
          "carbon_pricing"
        );
        break;

      case 19:
        askButtons(
          "Transition plan detail:",
          [{ value: "None" }, { value: "Qualitative" }, { value: "Quantified with interim KPIs" }, { value: "Capex-linked, board-approved" }],
          "transition_plan"
        );
        break;

      case 20:
        askButtons(
          "Energy management:",
          [{ value: "No program" }, { value: "Basic controls" }, { value: "Targets + metering" }, { value: "ISO/EnMS + continuous improve" }],
          "energy_management"
        );
        break;

      case 21:
        askButtons(
          "Renewables adoption:",
          [{ value: "0–10%" }, { value: "11–30%" }, { value: "31–50%" }, { value: ">50% or SBTi RE target" }],
          "renewables_adoption"
        );
        break;

      case 22:
        askButtons(
          "Electrification/decentralized energy:",
          [{ value: "None" }, { value: "Pilots" }, { value: "Multi-site rollout" }, { value: "Portfolio-scale (PV/HP/EV/Storage)" }],
          "electrification_energy"
        );
        break;

      case 23:
        askButtons(
          "Waste management:",
          [{ value: "Legal minimum" }, { value: "Compliance core streams" }, { value: "Reduction & diversion targets" }, { value: "Zero-waste/circular commitments" }],
          "waste_management"
        );
        break;

      case 24:
        askButtons(
          "Waste diverted (recycle/reuse/compost):",
          [{ value: "None / Don’t know" }, { value: "<20%" }, { value: "21-50%" }, { value: ">50%" }],
          "waste_diverted"
        );
        break;

      case 25:
        askButtons(
          "Product/service sustainability:",
          [{ value: "Not considered" }, { value: "Process tweaks" }, { value: "LCA-informed design" }, { value: "Circular/low-carbon portfolio" }],
          "product_sustainability"
        );
        break;

      case 26:
        askButtons(
          "Biodiversity & nature:",
          [{ value: "Not considered" }, { value: "Risks noted" }, { value: "Policies & TNFD-aligned steps" }, { value: "Strategy with targets & restoration" }],
          "biodiversity_nature"
        );
        break;

      case 27:
        askButtons(
          "Green building certifications:",
          [
  { value: "None" },
  { value: "EDGE" },
  { value: "BREEAM" },
  { value: "LEED" }
],
          "green_buildings"
        );
        break;

      case 28:
        askButtons(
          "Water measurement (withdrawal/consumption/discharge):",
          [{ value: "None" }, { value: "Partial" }, { value: "Full" }, { value: "Audited/externally assured" }],
          "water_measurement"
        );
        break;

      case 29:
        askButtons(
          "Nature-based solutions (check):",
          [{ value: "None" }, { value: "Rainwater" }, { value: "Green roofs" }, { value: "Wetlands" }],
          "nature_based_solutions"
        );
        break;

      case 30:
        askButtons(
          "Water risk (basin stress):",
          [{ value: "Not assessed" }, { value: "Screened" }, { value: "Integrated in plans" }, { value: "Site-level mitigations & targets" }],
          "water_risk"
        );
        break;

      case 31:
        askButtons(
          "Water efficiency/reuse:",
          [{ value: "None" }, { value: "KPIs set" }, { value: "Reuse <50% or tech upgrades" }, { value: "Reuse >50% + circular systems" }],
          "water_efficiency"
        );
        break;

      case 32:
        askButtons(
          "Supplier ESG expectations:",
          [{ value: "None" }, { value: "Tier-1 info" }, { value: "Code + assessments" }, { value: "Traceability + audits + co-innovation" }],
          "supplier_esg"
        );
        break;

      case 33:
        askButtons(
          "Purchased goods/services carbon:",
          [{ value: "No"  }, { value: "Planning" }, { value: "Yes (key cats)" }, { value: "Yes (broad cats) + supplier targets" }],
          "purchased_goods"
        );
        break;

      case 34:
        askButtons(
          "Sustainable procurement:",
          [{ value: "None" }, { value: "Informal" }, { value: "Formal policy" }, { value: "Category-level KPIs + sourcing levers" }],
          "sustainable_procurement"
        );
        break;

      case 35:
        askButtons(
          "ESG training:",
          [{ value: "None" }, { value: "Mandatory for all" }, { value: "Optional" }, { value: "ESG team only" }],
          "esg_training"
        );
        break;

      case 36:
        askButtons(
          "Staff involved in green initiatives:",
          [{ value: "<10%" }, { value: "11-30%" }, { value: "31-50%" }, { value: ">50%" }],
          "staff_green"
        );
        break;

      case 37:
        askButtons(
          "Data systems & dashboards:",
          [{ value: "None" }, { value: "Manual" }, { value: "Partial dashboards" }, { value: "Real-time/IoT + audit trail" }],
          "data_systems"
        );
        break;

      case 38:
        askButtons(
          "Reporting breadth & quality:",
          [{ value: "None" }, { value: "Internal only" }, { value: "Public (1+ standard)" }, { value: "Multi-standard + assurance" }],
          "reporting_quality"
        );
        break;

      case 39:
        askButtons(
          "Ratings/certifications:",
          [{ value: "None" }, { value: "Single (pilot)" }, { value: "Multiple" }, { value: "High-tier + continuous improvement" }],
          "ratings_certifications"
        );
        break;

      case 40:
        askButtons(
          "Green finance readiness:",
          [{ value: "None" }, { value: "Exploring" }, { value: "Framework drafted" }, { value: "Active SLB/Green Capex pipeline" }],
          "green_finance"
        );
        break;

      /* ======== Contact & Finalize ======== */
      case 41:
        appendBotMessage("✅ Almost done! Just a few more details to complete your sustainability roadmap.");
        setTimeout(() => {
          askInput("Please provide your valid email address:", "email", "fas fa-envelope");
        }, 600);
        break;

      case 42:
        askInput("Provide me your Full name", "Name");
        break;

      case 43:
        askInput("Provide us your contact No", "Phone_number");
        break;

      case 44:
        finalizeForm(); // compute score + submit
        break;

      default:
        finalizeForm();
        break;
    }

    step++;
  }, 800 + Math.random() * 600);
}

/* =========================================================
   UI HELPERS
========================================================= */
  function appendBotMessage(message) {
    const chatBox = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = "message bot";
    div.innerHTML = `<div class="bot-avatar avatar">🤖</div><div class="message-content">${message}</div>`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function appendUserMessage(message) {
    const chatBox = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = "message user";
    div.innerHTML = `<div class="user-avatar avatar">🧑</div><div class="message-content">${message}</div>`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function askInput(question, field, icon = "📝") {
    appendBotMessage(`${icon ? `<i class="${icon}"></i> ` : ""}${question}`);
    const inputArea = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = "input-wrapper";
    div.innerHTML = `
      <input type="text" id="userInput" class="input-box" placeholder="Type here..." autofocus />
    `;
    inputArea.appendChild(div);
    inputArea.scrollTop = inputArea.scrollHeight;

    const input = document.getElementById("userInput");
    input.focus();
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        handleInput(field);
      }
    });
  }

function askTextarea(question, field) {
  appendBotMessage(question);
  const chatBox = document.getElementById("chat-box");
  const div = document.createElement("div");
  div.className = "input-wrapper";
  div.innerHTML = `<textarea id="userTextarea" class="input-box" rows="4" placeholder="Type here..."></textarea>`;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;

  const textarea = document.getElementById("userTextarea");
  textarea.focus();
  textarea.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleTextarea(field);
    }
  });
}

function askButtons(question, options, field, opts = { score: true }) {
  appendBotMessage(question);
  const chatBox = document.getElementById("chat-box");
  const div = document.createElement("div");
  div.className = "button-group";

  options.forEach((opt, idx) => {
    const btn = document.createElement("button");
    btn.className = "chat-button";
    btn.innerHTML = `${opt.icon ? `<i class="${opt.icon}"></i> ` : ""}${opt.value}`;
    btn.onclick = () => {
      data[field] = opt.value;
      if (opts.score !== false) {
        // record score as the option index (0..n-1), higher index = higher maturity
        scores[field] = idx;
      }
      div.remove();
      nextStep(opt.value);
    };
    div.appendChild(btn);
  });

  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function askCheckboxes(question, options, field) {
  appendBotMessage(question);
  const chatBox = document.getElementById("chat-box");
  const div = document.createElement("div");
  div.className = "checkbox-group";

  options.forEach((opt) => {
    const label = document.createElement("label");
    label.innerHTML = `<input type="checkbox" value="${opt.value}"> ${opt.icon || ""} ${opt.value}`;
    div.appendChild(label);
  });

  const submitBtn = document.createElement("button");
  submitBtn.innerText = "Submit";
  submitBtn.className = "send-btn";
  submitBtn.onclick = () => {
    const checked = div.querySelectorAll("input[type='checkbox']:checked");
    const values = Array.from(checked).map((c) => c.value);

    data[field] = values;

    // Scoring: if "None" is selected -> 0 points; else # of selected (capped at 3)
    if (values.includes("None")) {
      scores[field] = 0;
    } else {
      scores[field] = Math.min(values.length, 3);
    }

    div.remove();
    nextStep(values.join(", "));
  };

  div.appendChild(submitBtn);
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

/* =========================================================
   INPUT HANDLERS
========================================================= */


function appendBotMessage(message, timeout = 0) {
  const chatBox = document.getElementById("chat-box");
  const div = document.createElement("div");
  div.className = "message bot temp-message"; // temp-message added for cleanup
  div.innerHTML = `<div class="bot-avatar avatar">🤖</div><div class="message-content">${message}</div>`;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;

  if (timeout > 0) {
    setTimeout(() => {
      div.remove();
    }, timeout);
  }
}

  function handleInput(field) {
    const val = document.getElementById("userInput").value.trim();
    if (!val) return;

    
    if (field === "email") {
      validateEmailWithAPI(val).then(isValid => {
        if (!isValid) {
          appendBotMessage("❌ The email address appears to be invalid. Please provide a valid email.", 1000);

          return;
        }
        data[field] = val;
        document.getElementById("userInput").parentElement.remove();
        nextStep(val);
      });
    } else {
      data[field] = val;
      document.getElementById("userInput").parentElement.remove();
      nextStep(val);
    }
  }

function handleTextarea(field) {
  const el = document.getElementById("userTextarea");
  if (!el) return;
  const val = el.value.trim();
  if (!val) return;
  data[field] = val;
  el.parentElement.remove();
  nextStep(val);
}

/* =========================================================
   TYPING INDICATOR
========================================================= */
function showTypingIndicator() {
  const chatBox = document.getElementById("chat-box");
  if (!chatBox) return;
  const typing = document.createElement("div");
  typing.className = "typing-indicator";
  typing.id = "typing-indicator";
  typing.innerHTML = `<div class="dot"></div><div class="dot"></div><div class="dot"></div>`;
  chatBox.appendChild(typing);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function hideTypingIndicator() {
  const typing = document.getElementById("typing-indicator");
  if (typing) typing.remove();
}

/* =========================================================
   SCORING
   - 34 scored questions (steps 7..40)
   - Each button question: score = option index (0..3 typically)
   - Checkboxes (nature_based_solutions): 0 if 'None', else count (capped 3)
   - Level: 1 (0–34), 2 (35–68), 3 (69+)
   - Confidence = (total * 2) / 204
   - Level names added
========================================================= */
function calculateScore() {
  const total = Object.values(scores).reduce((a, b) => a + b, 0);

  let level = 1;
  if (total >= 0 && total <= 5) level = 1;
  else if (total >= 6 && total <= 34) level = 2;
  else if (total >= 35 && total <= 68) level = 3;
  else if (total >= 69) level = 4; 

  // map level to name
  const levelNames = {
    1: "Starter",
    2: "Builder",
    3: "Performer", // (or keep "Builder" if you intended that)
    4: "Industry Leader",
  };

  const confidence = ((total * 2) / 204)*100;

  return { 
    total, 
    level, 
    confidence: parseFloat(confidence.toFixed(2)), 
    levelName: levelNames[level] || "Unknown" 
  };
}

/* =========================================================
   FINALIZE & SUBMIT
========================================================= */
function finalizeForm() {
  // Compute and attach score
  const result = calculateScore();
  data["score_total"] = result.total;
  data["score_level"] = result.level;
  data["score_level_name"] = result.levelName;
  data["confidence"] = result.confidence;

  appendBotMessage("✅ Thank you! Generating your sustainability roadmap...");

  // Fill hidden form & submit
  const chatDataEl = document.getElementById("chat-data");
  const clientEmailEl = document.getElementById("clientEmailInput");
  const chatForm = document.getElementById("chat-form");

  if (chatDataEl) chatDataEl.value = JSON.stringify(data);
  if (clientEmailEl) clientEmailEl.value = data["email"] || "";
  if (chatForm) chatForm.submit();
}

/* =========================================================
   EMAIL VALIDATION (calls /validate-email backend)
========================================================= */
async function validateEmailWithAPI(email) {
  try {
    const response = await fetch("/validate-email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    const result = await response.json();
    return !!result.valid;
  } catch (err) {
    console.error("Email validation failed:", err);
    return false;
  }
}