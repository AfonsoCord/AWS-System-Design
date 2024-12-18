/*import { useState, useEffect } from "react";
import api from "./api";
import Note from "./components/Note"
import ".src/styles/Home.css"*/
import {USERNAME} from "../constants";
import Loan from "../components/Empréstimo";

function Home() {

    return <div>
        <h1>Bem vindo, {localStorage.getItem(USERNAME)}</h1>
        <Loan route="/Home/" method="Home" />
    </div>

}

export default Home;