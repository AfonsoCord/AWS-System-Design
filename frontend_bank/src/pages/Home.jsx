import "../styles/Home.css"
import { USERNAME } from "../constants";
import { useNavigate } from "react-router-dom";

function Home() {
    const navigate = useNavigate();

    const handleLogout = () => { // Função para o botão de logout
        localStorage.clear();
        navigate("/BankLogin");
    };

    // estado dos empréstimos
    const handleLoanStatus = () => { 
        navigate("/loan_status_funcionarios");  
    };

    return (
        <div>
            <h1>Bem vindo, {localStorage.getItem(USERNAME)}</h1>
            <button className="logout" onClick={handleLogout}>Logout</button>
            <br/>
            <br/>
            <button className="logout" onClick={handleLoanStatus}>Estados dos empréstimos dos clientes</button> 
        </div>
    );
}

export default Home;
