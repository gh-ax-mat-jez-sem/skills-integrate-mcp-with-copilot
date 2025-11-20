document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  const loginModal = document.getElementById("login-modal");
  const loginForm = document.getElementById("login-form");
  const loginMessage = document.getElementById("login-message");
  const userIcon = document.getElementById("user-icon");
  const userStatus = document.getElementById("user-status");
  const closeModal = document.querySelector(".close");

  let isAuthenticated = false;
  let currentUser = null;

  // Check authentication status on load
  async function checkAuth() {
    try {
      const response = await fetch("/auth/status");
      const data = await response.json();
      isAuthenticated = data.authenticated;
      currentUser = data.username;
      updateUIForAuthState();
    } catch (error) {
      console.error("Error checking auth:", error);
    }
  }

  // Update UI based on authentication state
  function updateUIForAuthState() {
    if (isAuthenticated) {
      userStatus.textContent = `Logged in as ${currentUser}`;
      userStatus.classList.remove("hidden");
      userIcon.title = "Logout";
      // Show signup form for teachers
      document.getElementById("signup-container").style.display = "block";
    } else {
      userStatus.classList.add("hidden");
      userIcon.title = "Login";
      // Hide signup form for students
      document.getElementById("signup-container").style.display = "none";
    }
  }

  // Handle user icon click
  userIcon.addEventListener("click", async () => {
    if (isAuthenticated) {
      // Logout
      try {
        const response = await fetch("/logout", { method: "POST" });
        if (response.ok) {
          isAuthenticated = false;
          currentUser = null;
          updateUIForAuthState();
          fetchActivities(); // Refresh to hide delete buttons
          showMessage(messageDiv, "Logged out successfully", "success");
        }
      } catch (error) {
        console.error("Error logging out:", error);
      }
    } else {
      // Show login modal
      loginModal.classList.remove("hidden");
      loginModal.classList.add("show");
    }
  });

  // Close modal
  closeModal.addEventListener("click", () => {
    loginModal.classList.remove("show");
    loginModal.classList.add("hidden");
    loginForm.reset();
    loginMessage.classList.add("hidden");
  });

  // Close modal when clicking outside
  window.addEventListener("click", (event) => {
    if (event.target === loginModal) {
      loginModal.classList.remove("show");
      loginModal.classList.add("hidden");
      loginForm.reset();
      loginMessage.classList.add("hidden");
    }
  });

  // Handle login form submission
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
      const response = await fetch(
        `/login?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
        { method: "POST" }
      );

      const result = await response.json();

      if (response.ok) {
        isAuthenticated = true;
        currentUser = result.username;
        updateUIForAuthState();
        loginModal.classList.remove("show");
        loginModal.classList.add("hidden");
        loginForm.reset();
        fetchActivities(); // Refresh to show delete buttons
        showMessage(messageDiv, "Login successful!", "success");
      } else {
        showMessage(loginMessage, result.detail || "Login failed", "error");
      }
    } catch (error) {
      showMessage(loginMessage, "Login failed. Please try again.", "error");
      console.error("Error logging in:", error);
    }
  });

  // Helper function to show messages
  function showMessage(element, text, type) {
    element.textContent = text;
    element.className = type;
    element.classList.remove("hidden");

    setTimeout(() => {
      element.classList.add("hidden");
    }, 5000);
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

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
                      `<li>
                        <span class="participant-email">${email}</span>
                        ${isAuthenticated ? `<button class="delete-btn" data-activity="${name}" data-email="${email}">❌</button>` : ''}
                      </li>`
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
        messageDiv.textContent = result.message;
        messageDiv.className = "success";

        // Refresh activities list to show updated participants
        fetchActivities();
      } else {
        // Handle authentication error specifically
        if (response.status === 401) {
          messageDiv.textContent = "You must be logged in as a teacher to unregister students";
        } else {
          messageDiv.textContent = result.detail || "An error occurred";
        }
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to unregister. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
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
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();

        // Refresh activities list to show updated participants
        fetchActivities();
      } else {
        // Handle authentication error specifically
        if (response.status === 401) {
          messageDiv.textContent = "You must be logged in as a teacher to sign up students";
        } else {
          messageDiv.textContent = result.detail || "An error occurred";
        }
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  checkAuth();
  fetchActivities();
});
