/*import { useState, useEffect } from "react";
import api from "./api";
import Note from "./components/Note"*/
import "../styles/Home.css"
import {USERNAME} from "../constants";
import Loan from "../components/Empréstimo";
import { useNavigate } from "react-router-dom";

function Home() {

    const navigate = useNavigate();

    const handleLogout = () => { //botão de logout
        localStorage.clear();
        navigate("/login");
    };

    const handleEstado = () => {
        navigate("/loan_status");
    };

    return <div>
            <h1>Bem vindo, {localStorage.getItem(USERNAME)}</h1>
            <button className="logout" onClick={handleLogout}>Logout</button>
            <br/>
            <br/>
            <button className="logout" onClick={handleEstado}>Ver estado dos seus empréstimos</button>
            <Loan route="/Home/" method="Home" />
           </div>

}

export default Home;