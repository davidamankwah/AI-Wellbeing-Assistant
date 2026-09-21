import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function Login() {
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        username: "",
        password: "",
    });

    const [error, setError] = useState("");

    function handleChange(event){
        setFormData({
            ...formData,
            [event.target.name]: event.target.value,
        });
    }

    async function handleSubmit(event) {
        event.preventDefault();

        setError("");
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
            setError(
                "Unable to connect to the backend"
            );
          }
        }
    }
    
    return(
        <div>
            <h1>Login Account</h1>

            <form onSubmit={handleSubmit}>
              <div>
                <label>Username</label>
                <br />
                <input 
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
                />
                </div>  
                <br />

                <div>
                  <label>Password</label>
                  <br />
                    <input 
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                />
                </div>

                <br />

                <button type="submit">
                    Login
                </button>
            </form>

            {error && <p>{error}</p>}
        </div>
    );
}

export default Login;