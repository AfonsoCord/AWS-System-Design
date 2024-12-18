import Form from "../components/Form"
import { ACCESS_TOKEN } from "../constants";
import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";

function Login() {

    const navigate = useNavigate();

    useEffect(() => {
        if (localStorage.getItem(ACCESS_TOKEN)) {
            navigate("/Home", { replace: true });
        }
    }, [navigate]);

    return <Form route="/login/" method="login" />
}

export default Login