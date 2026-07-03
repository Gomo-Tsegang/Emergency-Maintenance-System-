// ============================================================
// admin.js
// Handles the Admin Dashboard functionality
// ============================================================

var API_BASE = "http://127.0.0.1:5000/api";
var employeeToDelete = null;

// ============================================================
// On page load: check session and load data
// ============================================================

window.onload = function () {
    checkSession();
};

function checkSession() {
    fetch(API_BASE + "/auth/session", {
        method: "GET",
        credentials: "include"
    })
    .then(function (response) {
        return response.json();
    })
    .then(function (data) {
        if (!data.logged_in || data.role !== "Admin") {
            window.location.href = "login.html";
        } else {
            document.getElementById("admin-name").textContent = data.name;
        }
    })
    .catch(function () {
        window.location.href = "login.html";
    });
}

// ============================================================
// Navigation between sections
// ============================================================

function showSection(sectionId, clickedItem) {
    var sections = document.querySelectorAll(".page-section");
    sections.forEach(function (section) {
        section.classList.remove("active");
    });

    var navItems = document.querySelectorAll(".sidebar-nav li");
    navItems.forEach(function (item) {
        item.classList.remove("active");
    });

    document.getElementById(sectionId).classList.add("active");
    clickedItem.classList.add("active");

    if (sectionId === "section-employees") {
        loadEmployees();
    }
}

// ============================================================
// Register Employee
// ============================================================

function showMessage(elementId, text, type) {
    var element = document.getElementById(elementId);
    element.className = "message " + type;
    element.textContent = text;
}

function registerEmployee() {
    var firstName = document.getElementById("reg-firstname").value.trim();
    var lastName = document.getElementById("reg-lastname").value.trim();
    var phone = document.getElementById("reg-phone").value.trim();
    var email = document.getElementById("reg-email").value.trim();
    var username = document.getElementById("reg-username").value.trim();
    var role = document.getElementById("reg-role").value;

    if (!firstName || !lastName || !email || !username || !role) {
        showMessage("register-message", "Please fill in all required fields.", "error");
        return;
    }

    var payload = {
        first_name: firstName,
        last_name: lastName,
        phone: phone,
        email: email,
        username: username,
        role: role
    };

    fetch(API_BASE + "/admin/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        credentials: "include",
        body: JSON.stringify(payload)
    })
    .then(function (response) {
        return response.json();
    })
    .then(function (data) {
        if (data.success) {
            showMessage("register-message", "Employee registered successfully. Login credentials have been sent by email.", "success");
            clearRegisterForm();
        } else {
            showMessage("register-message", data.message, "error");
        }
    })
    .catch(function () {
        showMessage("register-message", "Could not connect to the server.", "error");
    });
}

function clearRegisterForm() {
    document.getElementById("reg-firstname").value = "";
    document.getElementById("reg-lastname").value = "";
    document.getElementById("reg-phone").value = "";
    document.getElementById("reg-email").value = "";
    document.getElementById("reg-username").value = "";
    document.getElementById("reg-role").value = "";
}

// ============================================================
// Load All Employees
// ============================================================

function loadEmployees() {
    var tbody = document.getElementById("employees-table-body");
    tbody.innerHTML = "<tr><td colspan='8' class='no-data'>Loading...</td></tr>";

    fetch(API_BASE + "/admin/employees", {
        method: "GET",
        credentials: "include"
    })
    .then(function (response) {
        return response.json();
    })
    .then(function (data) {
        if (data.success) {
            renderEmployees(data.employees);
        } else {
            tbody.innerHTML = "<tr><td colspan='8' class='no-data'>Could not load employees.</td></tr>";
        }
    })
    .catch(function () {
        tbody.innerHTML = "<tr><td colspan='8' class='no-data'>Server error. Make sure the backend is running.</td></tr>";
    });
}

function renderEmployees(employees) {
    var tbody = document.getElementById("employees-table-body");

    if (employees.length === 0) {
        tbody.innerHTML = "<tr><td colspan='8' class='no-data'>No employees found.</td></tr>";
        return;
    }

    var html = "";

    employees.forEach(function (emp) {
        var badgeClass = "";
        if (emp.role === "Admin") {
            badgeClass = "badge-admin";
        } else if (emp.role === "Maintenance Manager") {
            badgeClass = "badge-manager";
        } else {
            badgeClass = "badge-accountable";
        }

        var deleteButton = "";
        if (emp.role !== "Admin") {
            deleteButton = "<button class='btn btn-danger btn-small' onclick='openDeleteModal(" + emp.id + ", \"" + emp.first_name + " " + emp.last_name + "\")'>Remove</button>";
        } else {
            deleteButton = "<span style='color: #aaaaaa; font-size: 12px;'>Protected</span>";
        }

        html += "<tr>";
        html += "<td>" + emp.id + "</td>";
        html += "<td>" + emp.first_name + "</td>";
        html += "<td>" + emp.last_name + "</td>";
        html += "<td>" + (emp.phone || "-") + "</td>";
        html += "<td>" + emp.email + "</td>";
        html += "<td>" + emp.username + "</td>";
        html += "<td><span class='badge " + badgeClass + "'>" + emp.role + "</span></td>";
        html += "<td>" + deleteButton + "</td>";
        html += "</tr>";
    });

    tbody.innerHTML = html;
}

// ============================================================
// Delete Employee Modal
// ============================================================

function openDeleteModal(id, name) {
    employeeToDelete = id;
    document.getElementById("delete-modal-text").textContent = "Are you sure you want to remove " + name + " from the system?";
    document.getElementById("delete-modal").classList.add("open");
}

function closeDeleteModal() {
    employeeToDelete = null;
    document.getElementById("delete-modal").classList.remove("open");
}

function confirmDelete() {
    if (!employeeToDelete) {
        return;
    }

    fetch(API_BASE + "/admin/employees/" + employeeToDelete, {
        method: "DELETE",
        credentials: "include"
    })
    .then(function (response) {
        return response.json();
    })
    .then(function (data) {
        closeDeleteModal();
        if (data.success) {
            showMessage("employees-message", "Employee removed successfully.", "success");
            loadEmployees();
        } else {
            showMessage("employees-message", data.message, "error");
        }
    })
    .catch(function () {
        closeDeleteModal();
        showMessage("employees-message", "Server error. Could not remove employee.", "error");
    });
}


function handleLogout() {
    fetch(API_BASE + "/auth/logout", {
        method: "POST",
        credentials: "include"
    })
    .then(function () {
        window.location.href = "login.html";
    })
    .catch(function () {
        window.location.href = "login.html";
    });
}
    