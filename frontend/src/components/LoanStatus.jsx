import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import { USERNAME } from "../constants";

function LoanStatus() {
    const [loans, setLoans] = useState([]);
    const [error, setError] = useState("");
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchLoanStatus = async () => {
            try {
                const username = localStorage.getItem(USERNAME);
                console.log("USERNAME from localStorage:", username);

                if (!username) {
                    setIsAuthenticated(false);
                    throw new Error("Utilizador não autenticado.");
                }

                setIsAuthenticated(true); // Usuário autenticado
                const response = await api.get("/loan_status/", {
                    params: { username },
                });
                console.log("Response da API:", response.data);
                setLoans(response.data.emprestimos || []);
            } catch (err) {
                console.error("Erro na chamada da API:", err.message);
                setError(err.message || "Erro ao processar os empréstimos.");
            }
        };

        fetchLoanStatus();
    }, []);

    return (
        <div>
            <h1>Estado dos seus Empréstimos</h1>
            {!isAuthenticated ? (
                <>
                    <p style={{ color: "red" }}>{error}</p>
                    <button onClick={() => navigate("/login")} className="form-button">
                        Faça Login
                    </button>
                </>
            ) : (
                <>
                    {loans.length > 0 ? (
                        <div>
                            <p>
                                Você possui <strong>{loans.length}</strong> empréstimo(s) em processamento.
                            </p>
                            {loans.map((loan, index) => (
                                <div
                                    key={index}
                                    style={{
                                        border: "1px solid #ccc",
                                        padding: "15px",
                                        margin: "10px 0",
                                        borderRadius: "8px",
                                        boxShadow: "0 2px 5px rgba(0,0,0,0.1)",
                                    }}
                                >
                                    <p><strong>Valor:</strong> {loan.valor}</p>
                                    <p><strong>Duração:</strong> {loan.duracao}</p>
                                    <p><strong>Estado:</strong> {loan.estado}</p>
                                </div>
                            ))}
                            {}
                            <div style={{ marginTop: "20px" }}>
                                <button
                                    onClick={() => navigate("/Home")}
                                    className="form-button"
                                    style={{ marginRight: "10px" }}
                                >
                                    Fazer novos empréstimos
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div>
                            <p>Não existem empréstimos disponíveis para exibição.</p>
                            <button
                                onClick={() => navigate("/Home")}
                                className="form-button"
                            >
                                Realizar empréstimos
                            </button>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}

export default LoanStatus;
