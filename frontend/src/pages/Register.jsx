
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../services/api";
import "../styles/style.css";

// Register component
function Register() {
    const navigate = useNavigate(); // Navigates to different pages

    // Stores the values entered into the registration form
    const [formData, setFormData] = useState({
        username: "",
        email: "",
        password: "",
    });

    // Stores successful and error messages
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    // Runs whenever the user types into an input field
    function handleChange(event) {
        setFormData({
            ...formData,
            [event.target.name]: event.target.value,
        });
    }

    // Runs when the registration form is submitted
    async function handleSubmit(event) {
        event.preventDefault();

        // Clear any previous messages
        setMessage("");
        setError("");
        setLoading(true);

        try {
            // Send the form data to the backend registration endpoint
            await api.post("/register", formData);

            // Display a success message
            setMessage(
                "Registration successful! You can now log in."
            );

            // Clear the form after successful registration
            setFormData({
                username: "",
                email: "",
                password: "",
            });

            // Wait 1.5 seconds before moving to the login page
            setTimeout(() => {
                navigate("/login");
            }, 1500);

        } catch (error) {
            if (error.response) {
                setError(
                    error.response.data.detail ||
                    "Registration failed."
                );
            } else {
                setError("Unable to connect to the backend.");
            }
        } finally {
            setLoading(false);
        }
    }

    // Display the styled registration page
    return (
        <div className="auth-page">
            <div className="auth-card">

                <div className="auth-logo">
                    Wellbeing Assistant
                </div>

                <h1>Create an Account</h1>

                <p className="auth-subtitle">
                    Welcome to Wellbeing Assistant – where you take
                    the first step towards improved mental wellbeing. 
                </p>

                {message && (
                    <p className="success-message" role="status">
                        {message}
                    </p>
                )}

                {error && (
                    <p className="error-message" role="alert">
                        {error}
                    </p>
                )}

                <form onSubmit={handleSubmit}>

                    {/* Username input */}
                    <div className="form-group">
                        <label htmlFor="username">
                            Username
                        </label>

                        <input
                            id="username"
                            type="text"
                            name="username"
                            placeholder="Enter your username"
                            value={formData.username}
                            onChange={handleChange}
                            autoComplete="username"
                            required
                        />
                    </div>

                    {/* Email input */}
                    <div className="form-group">
                        <label htmlFor="email">
                            Email Address
                        </label>

                        <input
                            id="email"
                            type="email"
                            name="email"
                            placeholder="Enter your email address"
                            value={formData.email}
                            onChange={handleChange}
                            autoComplete="email"
                            required
                        />
                    </div>

                    {/* Password input */}
                    <div className="form-group">
                        <label htmlFor="password">
                            Password
                        </label>

                        <input
                            id="password"
                            type="password"
                            name="password"
                            placeholder="Enter your password"
                            value={formData.password}
                            onChange={handleChange}
                            autoComplete="new-password"
                            required
                        />
                    </div>

                    {/* Register button */}
                    <button
                        type="submit"
                        className="primary-button"
                        disabled={loading || Boolean(message)}
                    >
                        {loading ? "Creating Account..." : "Register"}
                    </button>

                </form>

                {/* Link to the login page */}
                <p className="auth-footer">
                    Existing user?{" "}
                    <Link to="/login">
                        Login here
                    </Link>
                </p>

            </div>
        </div>
    );
}

export default Register;
