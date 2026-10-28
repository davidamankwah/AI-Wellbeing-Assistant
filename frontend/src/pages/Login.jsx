import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../services/api";
import "../styles/style.css";

function Login() {
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        username: "",
        password: "",
    });

    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    function handleChange(event) {
        setFormData({
            ...formData,
            [event.target.name]: event.target.value,
        });
    }

    async function handleSubmit(event) {
        event.preventDefault();

        setError("");
        setLoading(true);

        try {
            const response = await api.post("/login", formData);

            localStorage.setItem(
                "access_token",
                response.data.access_token
            );

            navigate("/dashboard");

        } catch (error) {
            if (error.response) {
                setError(
                    error.response.data.detail || "Login Failed."
                );
            } else {
                setError("Unable to connect to the backend");
            }
        } finally {
            setLoading(false);
        }
    }

    // Display the styled login page
    return (
        <div className="auth-page">
            <div className="auth-card">

                <div className="auth-logo">
                    Mental Wellbeing Assistant
                </div>

                <h1>Good to have you back!</h1>

                <p className="auth-subtitle">
                    Continue with your well-being journey 
                    by logging in to your account.
                </p>

                {error && (
                    <p className="error-message" role="alert">
                        {error}
                    </p>
                )}

                <form onSubmit={handleSubmit}>

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
                            autoComplete="current-password"
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        className="primary-button"
                        disabled={loading}
                    >
                        {loading ? "Logging in..." : "Login"}
                    </button>

                </form>

                <p className="auth-footer">
                    Don't have an account?{" "}
                    <Link to="/register">
                     Create an account
                    </Link>
                </p>

            </div>
        </div>
    );
}

export default Login;
