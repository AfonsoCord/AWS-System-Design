/*import { useState, useEffect } from "react";
import api from "./api";
import Note from "./components/Note"*/
import "../styles/Home.css"
import {USERNAME} from "../constants";
import { useNavigate } from "react-router-dom";

function Home() {

    const navigate = useNavigate();

    const handleLogout = () => { //botão de logout
        localStorage.clear();
        navigate("/BankLogin");
    };

    return <div>
            <h1>Bem vindo, {localStorage.getItem(USERNAME)}</h1>
            <button className="logout" onClick={handleLogout}>Logout</button>
           </div>

}

export default Home;