/*import { useState, useEffect } from "react";
import api from "./api";
import Note from "./components/Note"
import ".src/styles/Home.css"*/
import {USERNAME} from "../constants";

function Home() {

    return <div>
        <h1>Home</h1>
        <p>Bem vindo, {localStorage.getItem(USERNAME)}</p>
    </div>
}

export default Home;