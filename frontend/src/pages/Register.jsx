import { useState } from "react";
import {useNavigate} from "react-router-dom";
import api from "../services/api";

// Register component
function Register() {
    const navigate = useNavigate(); // navigates to different pages
     
    // Stores the values entered into the registration form
    const [formData, setFormData] = useState ({
        username: "",
        email: "",
        password: "",
    });

     // Stores a successful and error messages
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");

     // Runs whenever the user types into an input field
    function handleChange(event) {
        setFormData({
            ...formData,
            [event.target.name]: event.target.value,
        });
    }
     // Runs when the registration form is submitted
    async function handleSubmit(event){
        event.preventDefault();

        // Clear any previous messages
        setMessage("");
        setError("");

        try{
            // Send the form data to the backend registration endpoint
            await api.post("/register", formData);

            setMessage("RRegistration successful! You can now log in.");  // Display a success message

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
    // Display the registration page
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