import { useState } from "react";
import api from "../api";
import "../styles/Form.css";
import LoadingIndicator from "./LoadingIndicator";
import { useNavigate } from "react-router-dom";


function LoanForm({ route }) {
    const [Quantia, setQuantia] = useState("");
    const [Tempo, setTempo] = useState("");
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        setLoading(true);
        e.preventDefault();

        const loanData = {
            Quantia: parseFloat(Quantia),
            Tempo: parseInt(Tempo, 10),
        };

        try {
            const res = await api.post(route, loanData, {
                headers: {
                    "Content-Type": "application/json",
                },
            });
            alert("Loan submitted successfully!");
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
            {loading && <LoadingIndicator />}
            <button className="form-button" type="submit" onClick={() => navigate("/login")}>
                Simular
            </button>
        </form>
    );
}

export default LoanForm;
