import { useState } from "react";
import {useNavigate} from "react-router-dom";
import api from "../services/api";

function Register() {
    const navigate = useNavigate();

    const [formData, setFormData] = useState ({
        username: "",
        email: "",
        password: "",
    });

    const [message, setMessage] = useState("");
    const [error, setError] = useState("");

    function handleChange(event) {
        setFormData({
            ...formData,
            [event.target.name]: event.target.value,
        });
    }

    async function handleSubmit(event){
        event.preventDefault();

        setMessage("");
        setError("");

        try{
            await api.post("/register", formData);

            setMessage("RRegistration successful! You can now log in.");

            setFormData({
                username: "",
                email: "",
                password: "",
            });

            setTimeout(() => {
                navigate("/login");
            }, 1500);
        } catch(error) {
            if(error.response) {
                setError(
                    error.response.data.detail || "Registration failed."
                );
            } else{
                setError("Unable to connect to the backend.");
            }
        }
    }

    return(
        <div>
            <h1>Create an Account</h1>

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
            <label>Email</label>
            <br />
            <input
             type="email"
             name="email"
             value={formData.email}
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
                    Register
                </button>
            </form>

            {message && <p>{message}</p>}
            {error && <p>{error}</p>}
        </div>
    );


}

export default Register;