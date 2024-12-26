import React, { useEffect, useState } from "react";
import api from "../api";
import { ACCESS_TOKEN } from "../constants";

function LoanStatus() {
    const [loans, setLoans] = useState([]);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchLoanStatus = async () => {
            const token = localStorage.getItem(ACCESS_TOKEN);

            // verifica se o token existe
            if (!token) {
                setError("Token de autenticação ausente. Faça login como funcionário.");
                return;
            }

            try {
                const response = await api.get("/loan_status_funcionarios/", {
                    headers: {
                        Authorization: `Bearer ${token}`, 
                    },
                });

                console.log("Resposta da API:", response.data);
                setLoans(response.data.emprestimos || []);
            } catch (err) {
                console.error("Erro na chamada da API:", err.response?.data || err.message);
                setError(err.response?.data?.message || "Erro ao carregar os empréstimos dos clientes.");
            }
        };

        fetchLoanStatus();
    }, []);

    return (
        <div>
            <h1>Estado dos Empréstimos dos Clientes</h1>
            {error ? (
                <div>
                    <p style={{ color: "red" }}>{error}</p>
                </div>
            ) : loans.length > 0 ? (
                <div>
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
                            <p><strong>Usuário:</strong> {loan.usuario}</p>
                            <p><strong>Valor:</strong> {loan.valor}</p>
                            <p><strong>Duração:</strong> {loan.duracao}</p>
                            <p><strong>Estado:</strong> {loan.estado}</p>
                        </div>
                    ))}
                </div>
            ) : (
                <div>
                    <p>Não existem empréstimos disponíveis para exibição.</p>
                </div>
            )}
        </div>
    );
}

export default LoanStatus;
