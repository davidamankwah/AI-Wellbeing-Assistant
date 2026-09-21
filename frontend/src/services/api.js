import axios from "axios";

// Customised Axios instance
const api = axios.create({
     // The base URL of the FastAPI backend
    baseURL: "http://127.0.0.1:8000", 
})

export default api;