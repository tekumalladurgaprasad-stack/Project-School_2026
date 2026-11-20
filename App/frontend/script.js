// ================= CONFIG =================

// Where your FastAPI server is running (uvicorn main:app --reload)
const API_BASE = "http://127.0.0.1:8000";

// Field names must match schemas.py (Customer) exactly
const FIELDS = [
    "LIMIT_BAL", "SEX", "EDUCATION", "MARRIAGE", "AGE",
    "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6",
    "BILL_AMT1", "BILL_AMT2", "BILL_AMT3", "BILL_AMT4", "BILL_AMT5", "BILL_AMT6",
    "PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6"
];

const SEX_LABELS = { 1: "Male", 2: "Female" };
const EDUCATION_LABELS = {
    0: "Unknown", 1: "Graduate School", 2: "University",
    3: "High School", 4: "Others", 5: "Unknown", 6: "Unknown"
};
const MARRIAGE_LABELS = { 0: "Unknown", 1: "Married", 2: "Single", 3: "Others" };


// ================= HELPERS =================

function esc(value) {
    const div = document.createElement("div");
    div.textContent = String(value);
    return div.innerHTML;
}

function fmt(n) {
    return Number(n).toLocaleString();
}

async function api(path, options) {
    const res = await fetch(API_BASE + path, options);

    let data = null;
    try {
        data = await res.json();
    } catch (e) {
        // response had no JSON body
    }

    if (!res.ok) {
        const err = new Error("Request failed");
        err.status = res.status;
        err.data = data;
        throw err;
    }

    return data;
}

// Turns any error into a readable message
function errorMessage(err) {
    if (err.status === undefined) {
        return "Cannot reach the backend at " + API_BASE +
               ". Is uvicorn running? (If it is, check that CORS is enabled in main.py.)";
    }

    const detail = err.data && err.data.detail;

    // FastAPI/Pydantic validation errors (422) come as a list
    if (Array.isArray(detail)) {
        return detail.map(function(d) {
            const field = d.loc ? d.loc.slice(1).join(".") : "";
            return field + ": " + d.msg;
        }).join(" | ");
    }

    if (typeof detail === "string") {
        return detail;
    }

    return "Server returned error " + err.status + ".";
}

function showResult(box, type, title, html) {
    const icon = type === "success" ? "✓" : type === "error" ? "!" : "⌁";
    box.className = "result-box result-" + type;
    box.innerHTML =
        '<div class="result-message">' +
        '<span class="result-icon">' + icon + '</span>' +
        '<div><h3>' + title + '</h3>' + html + '</div>' +
        '</div>';
}

function setStatus(online, text) {
    document.getElementById("statusDot").classList.toggle("offline", !online);
    document.getElementById("statusText").textContent = text;
}


// ================= SIDEBAR NAVIGATION =================

const navItems = document.querySelectorAll(".nav-item");
const pages = document.querySelectorAll(".page-section");

navItems.forEach(function(item) {
    item.addEventListener("click", function() {
        const selectedPage = item.dataset.page;

        navItems.forEach(function(nav) {
            nav.classList.remove("active");
        });

        pages.forEach(function(page) {
            page.classList.remove("active");
        });

        item.classList.add("active");
        document.getElementById(selectedPage).classList.add("active");

        if (selectedPage === "dashboard" || selectedPage === "customers") {
            loadCustomers();
        }
    });
});


// ================= MANUAL / BULK TABS =================

const tabs = document.querySelectorAll(".prediction-tab");
const modes = {
    manual: document.getElementById("manualEntry"),
    bulk: document.getElementById("bulkUpload")
};

tabs.forEach(function(tab) {
    tab.addEventListener("click", function() {
        tabs.forEach(function(t) {
            t.classList.remove("active");
        });
        Object.values(modes).forEach(function(m) {
            m.classList.remove("active");
        });

        tab.classList.add("active");
        modes[tab.dataset.mode].classList.add("active");
    });
});


// ================= LOAD CUSTOMERS (dashboard + table) =================

async function loadCustomers() {
    const table = document.getElementById("customerTable");

    try {
        const data = await api("/customers");
        const customers = data.customers || [];

        setStatus(true, "Connected to backend");
        renderStats(customers);
        renderCustomerTable(customers);
    } catch (err) {
        if (err.status === undefined) {
            setStatus(false, "Backend offline");
        } else {
            setStatus(true, "Connected (GET /customers missing)");
        }

        const msg = err.status === 404 || err.status === 405
            ? "The backend has no GET /customers endpoint yet. Add it to main.py."
            : errorMessage(err);

        table.innerHTML =
            '<tr><td colspan="8" class="empty-state">' + esc(msg) + '</td></tr>';
    }
}

function renderStats(customers) {
    const total = customers.length;

    let limitSum = 0;
    let delayed = 0;

    customers.forEach(function(c) {
        limitSum += c.LIMIT_BAL;
        if (c.PAY_0 >= 1) {
            delayed++;
        }
    });

    document.getElementById("totalCustomers").textContent = fmt(total);
    document.getElementById("avgLimit").textContent = total ? fmt(Math.round(limitSum / total)) : "0";
    document.getElementById("delayedCustomers").textContent = fmt(delayed);
    document.getElementById("onTimeCustomers").textContent = fmt(total - delayed);
}

function renderCustomerTable(customers) {
    const table = document.getElementById("customerTable");

    if (customers.length === 0) {
        table.innerHTML =
            '<tr><td colspan="8" class="empty-state">No customer records available.</td></tr>';
        return;
    }

    table.innerHTML = customers.map(function(c, i) {
        const delayed = c.PAY_0 >= 1;
        const badge = delayed
            ? '<span class="badge badge-red">' + c.PAY_0 + ' month delay</span>'
            : '<span class="badge badge-green">On time</span>';

        return "<tr>" +
            "<td>" + (i + 1) + "</td>" +
            "<td>" + fmt(c.LIMIT_BAL) + "</td>" +
            "<td>" + c.AGE + "</td>" +
            "<td>" + (SEX_LABELS[c.SEX] || c.SEX) + "</td>" +
            "<td>" + (EDUCATION_LABELS[c.EDUCATION] || c.EDUCATION) + "</td>" +
            "<td>" + (MARRIAGE_LABELS[c.MARRIAGE] || c.MARRIAGE) + "</td>" +
            "<td>" + badge + "</td>" +
            "<td>" + fmt(c.BILL_AMT1) + "</td>" +
            "</tr>";
    }).join("");
}

document.getElementById("refreshCustomers").addEventListener("click", loadCustomers);


// ================= MANUAL ENTRY: POST /customers =================

const predictionForm = document.getElementById("predictionForm");
const predictionResult = document.getElementById("predictionResult");
const saveBtn = document.getElementById("saveBtn");

function readForm() {
    const payload = {};

    for (const name of FIELDS) {
        const value = Number(document.getElementById(name).value);

        if (!Number.isInteger(value)) {
            showResult(predictionResult, "error", "Invalid value",
                "<p>" + name + " must be a whole number.</p>");
            return null;
        }

        payload[name] = value;
    }

    return payload;
}

predictionForm.addEventListener("submit", async function(e) {
    e.preventDefault();

    const payload = readForm();
    if (!payload) return;

    saveBtn.disabled = true;
    saveBtn.textContent = "Saving...";

    try {
        const data = await api("/customers", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        showResult(predictionResult, "success", "Customer saved",
            "<p>" + esc(data.message) + "</p>" +
            '<p class="result-id">Customer ID: ' + esc(data.customer_id) + "</p>");

        predictionForm.reset();
        loadCustomers();
    } catch (err) {
        showResult(predictionResult, "error", "Could not save customer",
            "<p>" + esc(errorMessage(err)) + "</p>");
    } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = "Save Customer →";
    }
});

predictionForm.addEventListener("reset", function() {
    predictionResult.className = "result-box";
    predictionResult.innerHTML =
        '<div class="result-placeholder"><span>⌁</span>' +
        '<h3>Awaiting Submission</h3>' +
        '<p>Fill in the customer details and save them to the database.</p></div>';
});


// ================= BULK UPLOAD =================

const fileInput = document.getElementById("customerFile");
const fileNameBox = document.getElementById("fileName");
const uploadArea = document.getElementById("uploadArea");
const bulkForm = document.getElementById("bulkUploadForm");
const bulkResult = document.getElementById("bulkResult");
const bulkBtn = document.getElementById("bulkBtn");

const DEFAULT_FILE_TEXT = "Supported formats: CSV, JSON";

fileInput.addEventListener("change", function() {
    fileNameBox.textContent = fileInput.files.length
        ? fileInput.files[0].name
        : DEFAULT_FILE_TEXT;
});

// drag and drop
uploadArea.addEventListener("dragover", function(e) {
    e.preventDefault();
});

uploadArea.addEventListener("drop", function(e) {
    e.preventDefault();
    if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        fileNameBox.textContent = fileInput.files[0].name;
    }
});

bulkForm.addEventListener("reset", function() {
    fileNameBox.textContent = DEFAULT_FILE_TEXT;
    bulkResult.className = "result-box";
    bulkResult.innerHTML =
        '<div class="result-placeholder"><span>⌁</span>' +
        '<h3>Awaiting File Upload</h3>' +
        '<p>Upload customer records to begin.</p></div>';
});

// template download (CSV generated in the browser)
document.getElementById("downloadTemplate").addEventListener("click", function() {
    const sample = [
        20000, 2, 2, 1, 24,
        2, 2, -1, -1, -2, -2,
        3913, 3102, 689, 0, 0, 0,
        0, 689, 0, 0, 0, 0
    ];

    const csv = FIELDS.join(",") + "\n" + sample.join(",") + "\n";
    const blob = new Blob([csv], { type: "text/csv" });

    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "customer_template.csv";
    link.click();
    URL.revokeObjectURL(link.href);
});

// simple CSV parser (handles quotes)
function parseCSV(text) {
    const rows = [];
    let row = [];
    let cell = "";
    let inQuotes = false;

    for (let i = 0; i < text.length; i++) {
        const c = text[i];

        if (inQuotes) {
            if (c === '"') {
                if (text[i + 1] === '"') {
                    cell += '"';
                    i++;
                } else {
                    inQuotes = false;
                }
            } else {
                cell += c;
            }
        } else if (c === '"') {
            inQuotes = true;
        } else if (c === ",") {
            row.push(cell);
            cell = "";
        } else if (c === "\n") {
            row.push(cell);
            rows.push(row);
            row = [];
            cell = "";
        } else if (c !== "\r") {
            cell += c;
        }
    }

    if (cell !== "" || row.length) {
        row.push(cell);
        rows.push(row);
    }

    const header = rows.shift().map(function(h) { return h.trim(); });

    return rows
        .filter(function(r) {
            return r.some(function(v) { return v.trim() !== ""; });
        })
        .map(function(r) {
            const obj = {};
            header.forEach(function(h, i) {
                obj[h] = (r[i] || "").trim();
            });
            return obj;
        });
}

// keep only the fields the backend accepts (it rejects extras like ID / DEFAULT)
function buildPayload(record) {
    const payload = {};
    const missing = [];

    for (const name of FIELDS) {
        const raw = record[name];

        if (raw === undefined || raw === null || raw === "") {
            missing.push(name);
        } else {
            payload[name] = Number(raw);
        }
    }

    return { payload: payload, missing: missing };
}

bulkForm.addEventListener("submit", async function(e) {
    e.preventDefault();

    const file = fileInput.files[0];
    if (!file) return;

    let records;

    try {
        let text = await file.text();
        text = text.replace(/^\uFEFF/, ""); // strip BOM

        if (file.name.toLowerCase().endsWith(".json")) {
            const parsed = JSON.parse(text);
            records = Array.isArray(parsed) ? parsed : (parsed.customers || [parsed]);
        } else {
            records = parseCSV(text);
        }
    } catch (err) {
        showResult(bulkResult, "error", "Could not read file",
            "<p>Make sure it is a valid CSV or JSON file.</p>");
        return;
    }

    if (records.length === 0) {
        showResult(bulkResult, "error", "Empty file", "<p>No customer records found.</p>");
        return;
    }

    bulkBtn.disabled = true;
    bulkBtn.textContent = "Uploading...";

    let saved = 0;
    const failures = [];

    for (let i = 0; i < records.length; i++) {
        showResult(bulkResult, "info", "Uploading...",
            "<p>Saved " + saved + " of " + records.length + " records.</p>");

        const built = buildPayload(records[i]);

        if (built.missing.length) {
            failures.push("Row " + (i + 1) + ": missing " + built.missing.join(", "));
            continue;
        }

        try {
            await api("/customers", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(built.payload)
            });
            saved++;
        } catch (err) {
            failures.push("Row " + (i + 1) + ": " + errorMessage(err));

            // backend unreachable, no point trying the rest
            if (err.status === undefined) break;
        }
    }

    let html = "<p>" + saved + " of " + records.length + " records saved.</p>";

    if (failures.length) {
        html += '<ul class="result-list">' +
            failures.slice(0, 20).map(function(f) { return "<li>" + esc(f) + "</li>"; }).join("") +
            "</ul>";

        if (failures.length > 20) {
            html += "<p>...and " + (failures.length - 20) + " more failed rows.</p>";
        }
    }

    showResult(bulkResult, failures.length ? "error" : "success",
        failures.length ? "Upload finished with errors" : "Upload complete", html);

    bulkBtn.disabled = false;
    bulkBtn.textContent = "Upload & Save →";

    loadCustomers();
});


// ================= INIT =================

loadCustomers();
