let adminId = null;

document.addEventListener("DOMContentLoaded", () => {
  const adminIdInput = document.getElementById("admin-id");
  const verifyAdminBtn = document.getElementById("verify-admin");
  const authMessage = document.getElementById("auth-message");
  const dashboardContent = document.getElementById("dashboard-content");
  const createActivityBtn = document.getElementById("create-activity-btn");
  const createActivityForm = document.getElementById("create-activity-form");
  const cancelCreateBtn = document.getElementById("cancel-create");
  const activityForm = document.getElementById("activity-form");
  const activityMessage = document.getElementById("activity-message");

  // Verify admin access
  verifyAdminBtn.addEventListener("click", async () => {
    const inputValue = adminIdInput.value.trim();
    if (!inputValue) {
      showMessage(authMessage, "Please enter an admin ID", "error");
      return;
    }

    try {
      const response = await fetch("/admin/stats", {
        headers: {
          "X-User-ID": inputValue,
        },
      });

      if (response.ok) {
        adminId = inputValue;
        showMessage(authMessage, "Access granted! Loading dashboard...", "success");
        document.getElementById("admin-auth").style.display = "none";
        dashboardContent.classList.remove("hidden");
        loadDashboard();
      } else {
        showMessage(authMessage, "Access denied. Invalid admin ID.", "error");
      }
    } catch (error) {
      showMessage(authMessage, "Error verifying access. Please try again.", "error");
      console.error("Error verifying admin:", error);
    }
  });

  // Load dashboard data
  async function loadDashboard() {
    await Promise.all([
      loadStats(),
      loadPopularActivities(),
      loadUsers()
    ]);
  }

  // Load statistics
  async function loadStats() {
    try {
      const response = await fetch("/admin/stats", {
        headers: {
          "X-User-ID": adminId,
        },
      });

      if (response.ok) {
        const stats = await response.json();
        document.getElementById("total-students").textContent = stats.total_students;
        document.getElementById("total-activities").textContent = stats.total_activities;
        document.getElementById("total-enrollments").textContent = stats.total_enrollments;
        document.getElementById("capacity-utilization").textContent = `${stats.capacity_utilization}%`;
      }
    } catch (error) {
      console.error("Error loading stats:", error);
    }
  }

  // Load popular activities
  async function loadPopularActivities() {
    try {
      const response = await fetch("/admin/activities/popular", {
        headers: {
          "X-User-ID": adminId,
        },
      });

      if (response.ok) {
        const data = await response.json();
        displayPopularActivities(data.activities);
      }
    } catch (error) {
      console.error("Error loading popular activities:", error);
    }
  }

  // Display popular activities table
  function displayPopularActivities(activities) {
    const container = document.getElementById("popular-activities-table");
    
    if (activities.length === 0) {
      container.innerHTML = "<p>No activities found.</p>";
      return;
    }

    const table = document.createElement("table");
    table.className = "admin-table";
    table.innerHTML = `
      <thead>
        <tr>
          <th>Activity Name</th>
          <th>Enrollment</th>
          <th>Capacity</th>
          <th>Utilization</th>
          <th>Schedule</th>
        </tr>
      </thead>
      <tbody>
        ${activities.map((activity) => `
          <tr>
            <td><strong>${activity.name}</strong></td>
            <td>${activity.enrollment}</td>
            <td>${activity.capacity}</td>
            <td>
              <div class="utilization-bar">
                <div class="utilization-fill" style="width: ${activity.utilization}%"></div>
                <span class="utilization-text">${activity.utilization}%</span>
              </div>
            </td>
            <td>${activity.schedule}</td>
          </tr>
        `).join("")}
      </tbody>
    `;
    
    container.innerHTML = "";
    container.appendChild(table);
  }

  // Load users
  async function loadUsers() {
    try {
      const response = await fetch("/admin/users", {
        headers: {
          "X-User-ID": adminId,
        },
      });

      if (response.ok) {
        const data = await response.json();
        displayUsers(data.users);
      }
    } catch (error) {
      console.error("Error loading users:", error);
    }
  }

  // Display users table
  function displayUsers(users) {
    const container = document.getElementById("users-table");
    
    if (users.length === 0) {
      container.innerHTML = "<p>No users found.</p>";
      return;
    }

    const table = document.createElement("table");
    table.className = "admin-table";
    table.innerHTML = `
      <thead>
        <tr>
          <th>Student Email</th>
          <th>Activities Enrolled</th>
          <th>Activity Count</th>
        </tr>
      </thead>
      <tbody>
        ${users.map((user) => `
          <tr>
            <td>${user.email}</td>
            <td>${user.activities.join(", ")}</td>
            <td><span class="badge">${user.activity_count}</span></td>
          </tr>
        `).join("")}
      </tbody>
    `;
    
    container.innerHTML = "";
    container.appendChild(table);
  }

  // Show create activity form
  createActivityBtn.addEventListener("click", () => {
    createActivityForm.classList.remove("hidden");
    createActivityBtn.style.display = "none";
  });

  // Cancel create activity
  cancelCreateBtn.addEventListener("click", () => {
    createActivityForm.classList.add("hidden");
    createActivityBtn.style.display = "block";
    activityForm.reset();
  });

  // Create activity
  activityForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const activityData = {
      name: document.getElementById("activity-name").value,
      description: document.getElementById("activity-description").value,
      schedule: document.getElementById("activity-schedule").value,
      max_participants: parseInt(document.getElementById("activity-capacity").value),
    };

    try {
      const response = await fetch("/admin/activities", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-User-ID": adminId,
        },
        body: JSON.stringify(activityData),
      });

      const result = await response.json();

      if (response.ok) {
        showMessage(activityMessage, result.message, "success");
        activityForm.reset();
        createActivityForm.classList.add("hidden");
        createActivityBtn.style.display = "block";
        // Refresh dashboard
        loadDashboard();
      } else {
        showMessage(activityMessage, result.detail || "Error creating activity", "error");
      }
    } catch (error) {
      showMessage(activityMessage, "Failed to create activity. Please try again.", "error");
      console.error("Error creating activity:", error);
    }
  });

  // Helper function to show messages
  function showMessage(element, message, type) {
    element.textContent = message;
    element.className = type;
    element.classList.remove("hidden");

    setTimeout(() => {
      element.classList.add("hidden");
    }, 5000);
  }
});
