import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import { ACCESS_TOKEN, USERNAME } from "../constants";

function LoanStatus() {
    const [loans, setLoans] = useState([]);
    const [selectedHorarios, setSelectedHorarios] = useState({}); // horario escolhido pelo cliente
    const [error, setError] = useState("");
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchLoanStatus = async () => {
            try {
                const username = localStorage.getItem(USERNAME);
                const token = localStorage.getItem(ACCESS_TOKEN)

                if (!token) {
                    setIsAuthenticated(false);
                    throw new Error("Utilizador não autenticado.");
                }

                setIsAuthenticated(true);

                const response = await api.get("/loan_status/", {
                    headers: {
                        Authorization: `Bearer ${token}`, 
                    },
                    params: { username },
                });

                console.log("Response da API:", response.data);
                setLoans(response.data.emprestimos || []);
                setIsLoading(false);
            } catch (err) {
                console.error("Erro na chamada da API:", err.message);
                setError(err.message || "Erro ao processar os empréstimos.");
            }
        };

        fetchLoanStatus();
    }, []);

    const handleHorarioChange = (loanId, horario) => {
        setSelectedHorarios((prev) => ({
            ...prev,
            [loanId]: horario,
        }));
    };

    const handleSubmitHorario = async (loanId) => {
        const token = localStorage.getItem(ACCESS_TOKEN);
        const horario = selectedHorarios[loanId];

        if (!horario) {
            alert("Por favor, selecione um horário.");
            return;
        }

        try {
            const response = await api.post(
                "/escolher_horario/",
                { id: loanId, horarios: horario },
                {
                    headers: { Authorization: `Bearer ${token}` },
                }
            );
            alert(response.data.message);
            window.location.reload();
        } catch (err) {
            console.error(err.message);
            alert(err.response?.data?.message || "Erro ao selecionar horário.");
        }
    };

    return (
        <div>
            <h1>Estado dos seus Empréstimos</h1>
            {!isAuthenticated ? (
                <>
                    <p style={{ color: "red" }}>{error}</p>
                    <button onClick={() => navigate("/login")} className="form-button">
                        Faça Login.
                    </button>
                </>
            ) : isLoading ? (
                <p>A carregar os empréstimos...</p>
            ) : (
                <>
                    {loans.length > 0 ? (
                        <div>
                            <p>
                                Você possui <strong>{loans.length}</strong> pedido(s) de empréstimo(s):
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
                                    <p><strong>Tipo de empréstimo:</strong> {loan.tiposempr}</p>
                                    <p><strong>Valor:</strong> {loan.valor} €</p>
                                    <p><strong>Duração:</strong> {loan.duracao} meses</p>
                                    <p><strong>Estado:</strong> {loan.estado}</p>
                                    {loan.decisao && <p><strong>Decisão:</strong> {loan.decisao}</p>}
                                </div>
                            ))}
                            {}
                            <div style={{ marginTop: "20px" }}>
                                <button
                                    onClick={() => navigate("/Home")}
                                    className="form-button"
                                    style={{ marginRight: "10px" }}
                                >
                                    Fazer novo pedido de empréstimo
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div>
                            <p>Não existem pedidos de empréstimos disponíveis para exibição.</p>
                            <button
                                onClick={() => navigate("/Home")}
                                className="form-button"
                            >
                                Fazer pedido de empréstimo
                            </button>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}

export default LoanStatus;
