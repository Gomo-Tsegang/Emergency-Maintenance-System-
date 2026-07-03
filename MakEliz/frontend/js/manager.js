// ============================================================
// manager.js
// Handles the Maintenance Manager Dashboard
// ============================================================

var API_BASE = "http://127.0.0.1:5000/api";

// ============================================================
// On page load
// ============================================================

window.onload = function () {
    checkSession();
};

function checkSession() {
    fetch(API_BASE + "/auth/session", {
        method: "GET",
        credentials: "include"
    })
    .then(function (response) { return response.json(); })
    .then(function (data) {
        if (!data.logged_in || data.role !== "Maintenance Manager") {
            window.location.href = "login.html";
        } else {
            document.getElementById("manager-name").textContent = data.name;
            loadEMRequests();
        }
    })
    .catch(function () {
        window.location.href = "login.html";
    });
}

// ============================================================
// Navigation
// ============================================================

function showSection(sectionId, clickedItem) {
    document.querySelectorAll(".page-section").forEach(function (s) {
        s.classList.remove("active");
    });
    document.querySelectorAll(".sidebar-nav li").forEach(function (li) {
        li.classList.remove("active");
    });

    document.getElementById(sectionId).classList.add("active");
    clickedItem.classList.add("active");

    if (sectionId === "section-requests")    { loadEMRequests(); }
    if (sectionId === "section-assign")      { loadAssignDropdowns(); }
    if (sectionId === "section-assignments") { loadAssignments(); }
    if (sectionId === "section-received")    { loadReceivedForms(); }
    if (sectionId === "section-completions") { loadCompletionForms(); }
}

// ============================================================
// Show message helper
// ============================================================

function showMessage(elementId, text, type) {
    var el = document.getElementById(elementId);
    el.className = "message " + type;
    el.textContent = text;
}

// ============================================================
// EM Requests
// ============================================================

function loadEMRequests() {
    var tbody = document.getElementById("requests-table-body");
    tbody.innerHTML = "<tr><td colspan='6' class='no-data'>Loading...</td></tr>";

    fetch(API_BASE + "/manager/em-requests", {
        method: "GET",
        credentials: "include"
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
        if (!data.success || data.requests.length === 0) {
            tbody.innerHTML = "<tr><td colspan='6' class='no-data'>No open EM requests.</td></tr>";
            return;
        }

        var html = "";
        data.requests.forEach(function (req) {
            var badge = req.priority === "Very High" ? "badge-veryhigh"
                      : req.priority === "High"      ? "badge-high"
                      : "badge-normal";

            html += "<tr>";
            html += "<td>" + req.asset_sn + "</td>";
            html += "<td>" + req.asset_name + "</td>";
            html += "<td>" + req.request_date + "</td>";
            html += "<td>" + req.employee_full_name + "</td>";
            html += "<td>" + req.department + "</td>";
            html += "<td><span class='badge " + badge + "'>" + req.priority + "</span></td>";
            html += "</tr>";
        });
        tbody.innerHTML = html;
    })
    .catch(function () {
        tbody.innerHTML = "<tr><td colspan='6' class='no-data'>Server error.</td></tr>";
    });
}

// ============================================================
// Assign Asset - load dropdowns
// ============================================================

function loadAssignDropdowns() {
    var assetSelect = document.getElementById("assign-asset");
    var partySelect = document.getElementById("assign-party");

    assetSelect.innerHTML = "<option value=''>Loading assets...</option>";
    partySelect.innerHTML = "<option value=''>Loading parties...</option>";

    fetch(API_BASE + "/manager/all-assets", {
        method: "GET",
        credentials: "include"
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
        assetSelect.innerHTML = "<option value=''>-- Select Asset --</option>";
        if (data.success) {
            data.assets.forEach(function (asset) {
                assetSelect.innerHTML += "<option value='" + asset.id + "'>"
                    + asset.asset_sn + " - " + asset.asset_name
                    + (asset.department ? " (" + asset.department + ")" : "")
                    + "</option>";
            });
        }
    });

    fetch(API_BASE + "/manager/accountable-parties", {
        method: "GET",
        credentials: "include"
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
        partySelect.innerHTML = "<option value=''>-- Select Person --</option>";
        if (data.success) {
            data.parties.forEach(function (p) {
                partySelect.innerHTML += "<option value='" + p.id + "'>"
                    + p.first_name + " " + p.last_name + " - " + p.email
                    + "</option>";
            });
        }
    });
}

function submitAssignment() {
    var assetId   = document.getElementById("assign-asset").value;
    var partyId   = document.getElementById("assign-party").value;
    var date      = document.getElementById("assign-date").value;
    var notes     = document.getElementById("assign-notes").value.trim();

    if (!assetId || !partyId || !date) {
        showMessage("assign-message", "Please select an asset, a person, and a date.", "error");
        return;
    }

    fetch(API_BASE + "/manager/assign-asset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
            asset_id: assetId,
            assigned_to_employee_id: partyId,
            assigned_date: date,
            notes: notes
        })
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
        if (data.success) {
            showMessage("assign-message", "Asset assigned successfully.", "success");
            document.getElementById("assign-asset").value = "";
            document.getElementById("assign-party").value = "";
            document.getElementById("assign-date").value = "";
            document.getElementById("assign-notes").value = "";
        } else {
            showMessage("assign-message", data.message, "error");
        }
    })
    .catch(function () {
        showMessage("assign-message", "Server error. Could not assign asset.", "error");
    });
}

// ============================================================
// All Assignments
// ============================================================

function loadAssignments() {
    var tbody = document.getElementById("assignments-table-body");
    tbody.innerHTML = "<tr><td colspan='6' class='no-data'>Loading...</td></tr>";

    fetch(API_BASE + "/manager/assignments", {
        method: "GET",
        credentials: "include"
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
        if (!data.success || data.assignments.length === 0) {
            tbody.innerHTML = "<tr><td colspan='6' class='no-data'>No assignments found.</td></tr>";
            return;
        }

        var html = "";
        data.assignments.forEach(function (a) {
            var statusClass = a.status === "Completed"  ? "badge-normal"
                            : a.status === "In Progress" ? "badge-high"
                            : "badge-admin";

            html += "<tr>";
            html += "<td>" + a.asset_sn + "</td>";
            html += "<td>" + a.asset_name + "</td>";
            html += "<td>" + a.assigned_to + "</td>";
            html += "<td>" + a.assigned_date + "</td>";
            html += "<td>" + (a.notes || "-") + "</td>";
            html += "<td><span class='badge " + statusClass + "'>" + a.status + "</span></td>";
            html += "</tr>";
        });
        tbody.innerHTML = html;
    })
    .catch(function () {
        tbody.innerHTML = "<tr><td colspan='6' class='no-data'>Server error.</td></tr>";
    });
}

// ============================================================
// Work Received Forms
// ============================================================

function loadReceivedForms() {
    var tbody = document.getElementById("received-table-body");
    tbody.innerHTML = "<tr><td colspan='6' class='no-data'>Loading...</td></tr>";

    fetch(API_BASE + "/manager/received-forms", {
        method: "GET",
        credentials: "include"
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
        if (!data.success || data.forms.length === 0) {
            tbody.innerHTML = "<tr><td colspan='6' class='no-data'>No received forms submitted yet.</td></tr>";
            return;
        }

        var html = "";
        data.forms.forEach(function (f) {
            html += "<tr>";
            html += "<td>" + f.asset_sn + "</td>";
            html += "<td>" + f.asset_name + "</td>";
            html += "<td>" + f.received_by + "</td>";
            html += "<td>" + f.received_date + "</td>";
            html += "<td>" + (f.condition || "-") + "</td>";
            html += "<td>" + (f.comments || "-") + "</td>";
            html += "</tr>";
        });
        tbody.innerHTML = html;
    })
    .catch(function () {
        tbody.innerHTML = "<tr><td colspan='6' class='no-data'>Server error.</td></tr>";
    });
}



function loadCompletionForms() {
    var tbody = document.getElementById("completions-table-body");
    tbody.innerHTML = "<tr><td colspan='8' class='no-data'>Loading...</td></tr>";

    fetch(API_BASE + "/manager/completion-forms", {
        method: "GET",
        credentials: "include"
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
        if (!data.success || data.forms.length === 0) {
            tbody.innerHTML = "<tr><td colspan='8' class='no-data'>No completion forms submitted yet.</td></tr>";
            return;
        }

        var html = "";
        data.forms.forEach(function (f) {
            html += "<tr>";
            html += "<td>" + f.asset_sn + "</td>";
            html += "<td>" + f.asset_name + "</td>";
            html += "<td>" + f.submitted_by + "</td>";
            html += "<td>" + f.completion_date + "</td>";
            html += "<td>" + (f.work_done || "-") + "</td>";
            html += "<td>" + (f.problems || "-") + "</td>";
            html += "<td>" + (f.recommended_actions || "-") + "</td>";
            html += "<td>" + (f.final_condition || "-") + "</td>";
            html += "</tr>";
        });
        tbody.innerHTML = html;
    })
    .catch(function () {
        tbody.innerHTML = "<tr><td colspan='8' class='no-data'>Server error.</td></tr>";
    });
}

function handleLogout() {
    fetch(API_BASE + "/auth/logout", { method: "POST", credentials: "include" })
    .then(function () { window.location.href = "login.html"; })
    .catch(function () { window.location.href = "login.html"; });
}