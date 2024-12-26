import { useState } from "react";
import api from "../api";
import "../styles/Form.css";
import LoadingIndicator from "./LoadingIndicator";
import { useNavigate } from "react-router-dom";
import { ACCESS_TOKEN,DURACAO,VALOR } from "../constants";

function LoanForm({ route }) {
    const [valor, setvalor] = useState("");
    const [duracao, setduracao] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");  // Resetando o erro ao tentar submeter

        if (localStorage.getItem(ACCESS_TOKEN)) {
            return navigate("/Home");  // Navega para Home se já estiver autenticado
        }

        // Validação para garantir que os campos não estão vazios
        if (!valor || !duracao || isNaN(valor) || isNaN(duracao) || valor <= 0 || duracao <= 0) {
            setError("Por favor, preencha todos os campos corretamente.");
            setLoading(false);
            return;
        }

        const loanData = {
            valor: parseFloat(valor),
            duracao: parseInt(duracao),
        };

        try {
            // Enviar a requisição assíncrona
            const response = await api.post("/loan_simulator/", loanData, {
                headers: {
                    "Content-Type": "application/json",
                },
            },
            localStorage.setItem(DURACAO,loanData.duracao),
            localStorage.setItem(VALOR,loanData.valor));
            alert(error.response?.data?.message || "Para prosseguir necessita de fazer Login!");
            navigate("/login");  // Navega para login

        } catch (error) {
            alert(error.response?.data?.message || "An error occurred.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="form-container">
            <h1>Simulador do Empréstimo</h1>
            <input
                className="form-input"
                type="number"
                value={valor}
                onChange={(e) => setvalor(e.target.value)}
                placeholder="Quantia do empréstimo"
                required
            />
            <input
                className="form-input"
                type="number"
                value={duracao}
                onChange={(e) => setduracao(e.target.value)}
                placeholder="Duração do empréstimo"
                required
            />
            {error && <p style={{ color: "red" }}>{error}</p>}
            {loading && <LoadingIndicator />}
            <button
                className="form-button"
                type="submit"
                disabled={!valor || !duracao || isNaN(valor) || isNaN(duracao) || valor <= 0 || duracao <= 0 || loading}
            >
                {loading ? "Processando..." : "Simular"}
            </button>
        </form>
    );
}

export default LoanForm;