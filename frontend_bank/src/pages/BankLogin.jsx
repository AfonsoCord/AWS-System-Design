import LoginForm from "../components/LoginForm"
import { ACCESS_TOKEN } from "../constants";
import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";

function BankLogin() {

    const navigate = useNavigate();

    useEffect(() => {
        if (localStorage.getItem(ACCESS_TOKEN)) {
            navigate("/Home", { replace: true });
        }
    }, [navigate]);

    return <LoginForm route="/BankLogin/" method="login"/>
}

export default BankLogin