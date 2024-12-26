import React from "react";
import { useNavigate } from "react-router-dom";
import LoanStatus from "../components/LoanStatus";

function LoanStatusPage() {
    const navigate = useNavigate(); 

    const goBack = () => {
        navigate('/Home'); 
    };

    return (
        <div>
            <LoanStatus />
            <button onClick={goBack}>Voltar</button> 
        </div>
    );
}

export default LoanStatusPage;
