import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import "../styles/style.css";

function Dashboard() {
  const navigate = useNavigate();

  // Stores the logged-in user's detail
  const [user, setUser] = useState(null);

  // Keep track loading and error states
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Log out method
  function handleLogout() {
    localStorage.removeItem("access_token"); //removes jwt token
    navigate("/login", { replace: true }); //sign out the user and back to login 
  }

  // Get the logged-in user's details
  useEffect(() => {
    let active = true;

    async function fetchUser() {
      const token = localStorage.getItem("access_token");

      // Redirection, if token does nit exists
      if (!token) {
        navigate("/login", { replace: true });
        return;
      }

      try {
        // JWT token is passed to FastAPI
        const response = await api.get("/users/me", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        // Store the received user data
        if (active) {
          setUser(response.data);
        }
      } catch (err) {
        if (!active) return;

        // Invalid or expired JWT
        if ([401, 403].includes(err.response?.status)) {
          localStorage.removeItem("access_token");
          navigate("/login", { replace: true });
        } else {
          setError("Unable to load your profile. Please try again.");
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    fetchUser();

    return () => {
      active = false;
    };
  }, [navigate]);

  // Display loading state while validating the token
  if (loading) {
    return (
      <div className="dashboard-page">
        <main className="dashboard-content">
          <p>Loading your dashboard...</p>
        </main>
      </div>
    );
  }

  // Display error if the request fails
  if (error) {
    return (
      <div className="dashboard-page">
        <main className="dashboard-content">
          <p className="error-message" role="alert">{error}</p>
          <button onClick={() => window.location.reload()}>
            Try Again
          </button>
          <button onClick={handleLogout}>Log Out</button>
        </main>
      </div>
    );
  }

  // Display the dashboard 
  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div className="auth-logo" style={{ marginBottom: 0 }}>
          Wellbeing Assistant
        </div>

        <button onClick={handleLogout}>
          Log Out
        </button>
      </header>

      <main className="dashboard-content">
        <h1>Welcome back, {user?.username}!</h1>

        <p className="dashboard-subtitle">
          A conducive environment for reflection,
           checking in, and taking care of yourself.
        </p>

        <div className="user-profile">
          <h2>Your Profile</h2>
          <p><strong>Username:</strong> {user?.username}</p>
          <p><strong>Email:</strong> {user?.email}</p>
        </div>

        <div className="dashboard-grid">
          <div className="feature-card">
            <h2>Wellbeing Chat</h2>
            <p>
              Have supportive conversations with your
              local AI wellbeing assistant.
            </p>
            <span className="feature-status">Coming soon</span>
          </div>

          <div className="feature-card">
            <h2>Mood Check-in</h2>
            <p>
              Reflect on how you're feeling and build
              awareness of your wellbeing.
            </p>
            <span className="feature-status">Coming soon</span>
          </div>

          <div className="feature-card">
            <h2>Support Resources</h2>
            <p>
              Explore wellbeing guidance and appropriate
              sources of additional support.
            </p>
            <span className="feature-status">Coming soon</span>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Dashboard;