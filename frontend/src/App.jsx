import { BrowserRouter, Routes, Route } from "react-router-dom";
import Register from "./pages/Register";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/login"  element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />



        <Route
          path="/"
          element={<h1>Welcome to the Wellbeing Assistant</h1>}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;