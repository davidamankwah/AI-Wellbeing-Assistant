import { Navigate } from "react-router-dom";

function PrivateRoute({children}){
    const tokens = localStorage.getItem("access_token");

    if(!tokens){
        return <Navigate to="/login" replace />
    }
   return children;
}

export default PrivateRoute;