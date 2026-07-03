// ============================================================
// accountable.js
// Handles the Accountable Party Dashboard
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
        if (!data.logged_in || data.role !== "Accountable Party") {
            window.location.href = "login.html";
        } else {
            document.getElementById("accountable-name").textContent = data.name;
            loadMyAssets();
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

    if (sectionId === "section-assets")          { loadMyAssets(); }
    if (sectionId === "section-assignments")     { loadMyAssignments(); }
    if (sectionId === "section-received-form")   { loadAssignmentDropdowns(); }
    if (sectionId === "section-completion-form") { loadAssignmentDropdowns(); }
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
// My Assets (read-only)
// ============================================================

function loadMyAssets() {
    var tbody = document.getElementById("assets-table-body");
    tbody.innerHTML = "<tr><td colspan='7' class='no-data'>Loading...</td></tr>";

    fetch(API_BASE + "/accountable/my-assets", {
        method: "GET",
        credentials: "include"
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
        if (!data.success || data.assets.length === 0) {
            tbody.innerHTML = "<tr><td colspan='7' class='no-data'>No assets found.</td></tr>";
            return;
        }

        var html = "";
        data.assets.forEach(function (asset) {
            html += "<tr>";
            html += "<td>" + asset.asset_sn + "</td>";
            html += "<td>" + asset.asset_name + "</td>";
            html += "<td>" + (asset.department || "-") + "</td>";
            html += "<td>" + (asset.location || "-") + "</td>";
            html += "<td>" + (asset.asset_group || "-") + "</td>";
            html += "<td>" + (asset.description || "-") + "</td>";
            html += "<td>" + (asset.warranty_date || "-") + "</td>";
            html += "</tr>";
        });
        tbody.innerHTML = html;
    })
    .catch(function () {
        tbody.innerHTML = "<tr><td colspan='7' class='no-data'>Server error.</td></tr>";
    });
}

function loadMyAssignments() {
    var tbody = document.getElementById("my-assignments-table-body");
    tbody.innerHTML = "<tr><td colspan='8' class='no-data'>Loading...</td></tr>";

    fetch(API_BASE + "/accountable/my-assignments", {
        method: "GET",
        credentials: "include"
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
        if (!data.success || data.assignments.length === 0) {
            tbody.innerHTML = "<tr><td colspan='8' class='no-data'>No assignments found.</td></tr>";
            return;
        }

        var html = "";
        data.assignments.forEach(function (a) {
            var statusClass = a.status === "Completed"   ? "badge-normal"
                            : a.status === "In Progress" ? "badge-high"
                            : "badge-admin";

            var receivedBadge = a.received_form_filled
                ? "<span class='badge badge-normal'>Submitted</span>"
                : "<span class='badge badge-veryhigh'>Pending</span>";

            var completionBadge = a.completion_form_filled
                ? "<span class='badge badge-normal'>Submitted</span>"
                : "<span class='badge badge-veryhigh'>Pending</span>";

            html += "<tr>";
            html += "<td>" + a.asset_sn + "</td>";
            html += "<td>" + a.asset_name + "</td>";
            html += "<td>" + a.assigned_by + "</td>";
            html += "<td>" + a.assigned_date + "</td>";
            html += "<td>" + (a.notes || "-") + "</td>";
            html += "<td><span class='badge " + statusClass + "'>" + a.status + "</span></td>";
            html += "<td>" + receivedBadge + "</td>";
            html += "<td>" + completionBadge + "</td>";
            html += "</tr>";
        });
        tbody.innerHTML = html;
    })
    .catch(function () {
        tbody.innerHTML = "<tr><td colspan='8' class='no-data'>Server error.</td></tr>";
    });
}

function loadAssignmentDropdowns() {
    fetch(API_BASE + "/accountable/my-assignments", {
        method: "GET",
        credentials: "include"
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
        var receivedSelect    = document.getElementById("received-assignment");
        var completionSelect  = document.getElementById("completion-assignment");

        receivedSelect.innerHTML   = "<option value=''>-- Select Assignment --</option>";
        completionSelect.innerHTML = "<option value=''>-- Select Assignment --</option>";

        if (data.success) {
            data.assignments.forEach(function (a) {
                var label = a.asset_sn + " - " + a.asset_name + " (Assigned: " + a.assigned_date + ")";

                if (!a.received_form_filled) {
                    receivedSelect.innerHTML += "<option value='" + a.id + "'>" + label + "</option>";
                }

                if (a.received_form_filled && !a.completion_form_filled) {
                    completionSelect.innerHTML += "<option value='" + a.id + "'>" + label + "</option>";
                }
            });

            if (receivedSelect.options.length === 1) {
                receivedSelect.innerHTML = "<option value=''>No pending received forms</option>";
            }
            if (completionSelect.options.length === 1) {
                completionSelect.innerHTML = "<option value=''>No pending completion forms</option>";
            }
        }
    })
    .catch(function () {
        console.log("Could not load assignments for dropdowns.");
    });
}

function submitReceivedForm() {
    var assignmentId = document.getElementById("received-assignment").value;
    var date         = document.getElementById("received-date").value;
    var condition    = document.getElementById("received-condition").value.trim();
    var comments     = document.getElementById("received-comments").value.trim();

    if (!assignmentId || !date) {
        showMessage("received-form-message", "Please select an assignment and enter the date received.", "error");
        return;
    }

    fetch(API_BASE + "/accountable/submit-received", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
            assignment_id: assignmentId,
            received_date: date,
            condition_on_receiving: condition,
            comments_on_receiving: comments
        })
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
        if (data.success) {
            showMessage("received-form-message", "Work received form submitted successfully.", "success");
            document.getElementById("received-assignment").value = "";
            document.getElementById("received-date").value = "";
            document.getElementById("received-condition").value = "";
            document.getElementById("received-comments").value = "";
            loadAssignmentDropdowns();
        } else {
            showMessage("received-form-message", data.message, "error");
        }
    })
    .catch(function () {
        showMessage("received-form-message", "Server error. Could not submit form.", "error");
    });
}

function submitCompletionForm() {
    var assignmentId    = document.getElementById("completion-assignment").value;
    var date            = document.getElementById("completion-date").value;
    var workDone        = document.getElementById("completion-work-done").value.trim();
    var problems        = document.getElementById("completion-problems").value.trim();
    var recommended     = document.getElementById("completion-recommended").value.trim();
    var finalCondition  = document.getElementById("completion-final-condition").value.trim();

    if (!assignmentId || !date || !workDone) {
        showMessage("completion-form-message", "Please select an assignment, enter the date, and describe the work done.", "error");
        return;
    }

    fetch(API_BASE + "/accountable/submit-completion", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
            assignment_id: assignmentId,
            completion_date: date,
            work_done_description: workDone,
            problems_encountered: problems,
            recommended_actions: recommended,
            final_condition: finalCondition
        })
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
        if (data.success) {
            showMessage("completion-form-message", "Completion form submitted to the Manager successfully.", "success");
            document.getElementById("completion-assignment").value = "";
            document.getElementById("completion-date").value = "";
            document.getElementById("completion-work-done").value = "";
            document.getElementById("completion-problems").value = "";
            document.getElementById("completion-recommended").value = "";
            document.getElementById("completion-final-condition").value = "";
            loadAssignmentDropdowns();
        } else {
            showMessage("completion-form-message", data.message, "error");
        }
    })
    .catch(function () {
        showMessage("completion-form-message", "Server error. Could not submit form.", "error");
    });
}

function handleLogout() {
    fetch(API_BASE + "/auth/logout", { method: "POST", credentials: "include" })
    .then(function () { window.location.href = "login.html"; })
    .catch(function () { window.location.href = "login.html"; });
}