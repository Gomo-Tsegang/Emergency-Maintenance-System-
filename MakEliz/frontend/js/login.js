const API_BASE = "/api";

function showMessage(elementID, text, type) {
    var element = document.getElementById(elementID);
    element.className = "message " + type;
    element.textContent = text
}

function handleLogin(){
    var username = document.getElementById("username").value.trim();
    var password = document.getElementById("password").value.trim();

    if (username === "" || password === "") {
        showMessage("login-message", "please enter your username and password.", "error");
        return;
    }

    fetch(API_BASE + "/auth/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        credentials: "include",
        body: JSON.stringify({ username: username, password: password })
    })

    .then(function(response) {
        if (!response.ok) {
            return response.text().then(function(text) {
                throw new Error("Server returned " + response.status + ": " + text);
            });
        }
        return response.json();
    })
    .then(function(data) {
        if (data.success) {
            var role = data.role;

            if (role === "Admin") {
                window.location.href = "admin_dashboard.html";
            } else if (role === "Maintenance Manager") {
                window.location = "manager_dashboard.html";
            } else if (role === "Accountable Party") {
                window.location = "accountable_dashboard.html";
            } else {
                showMessage("login-message", "Unknown role. Contact your administrator.", "error");
            }
        } else {
            showMessage("login-message", data.message, "error");
        }
    })

    .catch(function(error) {
        console.error(error);
        showMessage("login-message", "Could not connect to the server: " + error.message, "error");
    });
}


document.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        handleLogin();
    }
});
