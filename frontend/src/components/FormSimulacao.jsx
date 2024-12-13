import { useState } from "react";
import api from "../api";
import "../styles/Form.css";
import LoadingIndicator from "./LoadingIndicator";
import { useNavigate } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN} from "../constants";

function LoanForm({ route }) {
    const [Quantia, setQuantia] = useState("");
    const [Tempo, setTempo] = useState("");
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
        if (!Quantia || !Tempo || isNaN(Quantia) || isNaN(Tempo) || Quantia <= 0 || Tempo <= 0) {
            setError("Por favor, preencha todos os campos corretamente.");
            setLoading(false);
            return;
        }

        const loanData = {
            Quantia: parseFloat(Quantia),
            Tempo: parseInt(Tempo, 10),
        };

        try {
            // Enviar a requisição assíncrona
            const response = await api.post("/loan_simulator/", loanData, {
                headers: {
                    "Content-Type": "application/json",
                },
            });

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
                value={Quantia}
                onChange={(e) => setQuantia(e.target.value)}
                placeholder="Quantia do empréstimo"
                required
            />
            <input
                className="form-input"
                type="number"
                value={Tempo}
                onChange={(e) => setTempo(e.target.value)}
                placeholder="Duração do empréstimo"
                required
            />
            {error && <p style={{ color: "red" }}>{error}</p>}
            {loading && <LoadingIndicator />}
            <button
                className="form-button"
                type="submit"
                disabled={!Quantia || !Tempo || isNaN(Quantia) || isNaN(Tempo) || Quantia <= 0 || Tempo <= 0 || loading}
            >
                {loading ? "Processando..." : "Simular"}
            </button>
        </form>
    );
}

export default LoanForm;