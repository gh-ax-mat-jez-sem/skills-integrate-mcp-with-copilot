document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  const loginForm = document.getElementById("login-form");
  const loginMessage = document.getElementById("login-message");
  const userInfo = document.getElementById("user-info");
  const currentUserEmail = document.getElementById("current-user-email");
  const viewScheduleBtn = document.getElementById("view-schedule-btn");
  const scheduleContainer = document.getElementById("schedule-container");
  const scheduleList = document.getElementById("schedule-list");
  const activitiesContainer = document.getElementById("activities-container");
  const signupContainer = document.getElementById("signup-container");
  const backToActivitiesBtn = document.getElementById("back-to-activities-btn");

  let loggedInUser = null;

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Clear activity select
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft =
          details.max_participants - details.participants.length;

        // Create participants HTML with delete icons instead of bullet points
        const participantsHTML =
          details.participants.length > 0
            ? `<div class="participants-section">
              <h5>Participants:</h5>
              <ul class="participants-list">
                ${details.participants
                  .map(
                    (email) =>
                      `<li><span class="participant-email">${email}</span><button class="delete-btn" data-activity="${name}" data-email="${email}">❌</button></li>`
                  )
                  .join("")}
              </ul>
            </div>`
            : `<p><em>No participants yet</em></p>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-container">
            ${participantsHTML}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      // Add event listeners to delete buttons
      document.querySelectorAll(".delete-btn").forEach((button) => {
        button.addEventListener("click", handleUnregister);
      });
    } catch (error) {
      activitiesList.innerHTML =
        "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Function to fetch user schedule
  async function fetchUserSchedule(email) {
    try {
      const response = await fetch(`/users/${encodeURIComponent(email)}/schedule`);
      
      if (!response.ok) {
        throw new Error("Failed to fetch schedule");
      }

      const data = await response.json();

      // Clear schedule list
      scheduleList.innerHTML = "";

      if (data.schedule.length === 0) {
        scheduleList.innerHTML = "<p>You are not enrolled in any activities yet.</p>";
      } else {
        data.schedule.forEach((activity) => {
          const activityCard = document.createElement("div");
          activityCard.className = "activity-card";
          activityCard.innerHTML = `
            <h4>${activity.name}</h4>
            <p>${activity.description}</p>
            <p><strong>Schedule:</strong> ${activity.schedule}</p>
          `;
          scheduleList.appendChild(activityCard);
        });
      }

      // Show schedule container, hide others
      scheduleContainer.classList.remove("hidden");
      activitiesContainer.classList.add("hidden");
      signupContainer.classList.add("hidden");
    } catch (error) {
      showMessage(loginMessage, "Failed to load schedule. Please try again.", "error");
      console.error("Error fetching schedule:", error);
    }
  }

  // Handle login form submission
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("login-email").value;

    try {
      const response = await fetch(
        `/users/login?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        loggedInUser = result.user;
        currentUserEmail.textContent = loggedInUser.email;
        userInfo.classList.remove("hidden");
        loginForm.classList.add("hidden");
        showMessage(loginMessage, result.message, "success");
      } else {
        showMessage(loginMessage, result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage(loginMessage, "Failed to login. Please try again.", "error");
      console.error("Error logging in:", error);
    }
  });

  // View schedule button handler
  viewScheduleBtn.addEventListener("click", () => {
    if (loggedInUser) {
      fetchUserSchedule(loggedInUser.email);
    }
  });

  // Back to activities button handler
  backToActivitiesBtn.addEventListener("click", () => {
    scheduleContainer.classList.add("hidden");
    activitiesContainer.classList.remove("hidden");
    signupContainer.classList.remove("hidden");
  });

  // Handle unregister functionality
  async function handleUnregister(event) {
    const button = event.target;
    const activity = button.getAttribute("data-activity");
    const email = button.getAttribute("data-email");

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(
          activity
        )}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(messageDiv, result.message, "success");

        // Refresh activities list to show updated participants
        fetchActivities();
      } else {
        showMessage(messageDiv, result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage(messageDiv, "Failed to unregister. Please try again.", "error");
      console.error("Error unregistering:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(
          activity
        )}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(messageDiv, result.message, "success");
        signupForm.reset();

        // Refresh activities list to show updated participants
        fetchActivities();
      } else {
        showMessage(messageDiv, result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage(messageDiv, "Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  // Helper function to show messages
  function showMessage(element, text, type) {
    element.textContent = text;
    element.className = type;
    element.classList.remove("hidden");

    // Hide message after 5 seconds
    setTimeout(() => {
      element.classList.add("hidden");
    }, 5000);
  }

  // Initialize app
  fetchActivities();
});
