import React, { useEffect, useState } from "react";
import api from "../api";
import { ACCESS_TOKEN } from "../constants";

function LoanStatus() {
    const [loans, setLoans] = useState([]);
    const [loanDecisions, setLoanDecisions] = useState({});
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchLoanStatus = async () => {
            const token = localStorage.getItem(ACCESS_TOKEN);

            if (!token) {
                setError("Token de autenticação ausente. Faça login como funcionário.");
                return;
            }

            try {
                const response = await api.get("/loan_status_funcionarios/", {
                    headers: { Authorization: `Bearer ${token}` },
                });

                console.log("Resposta da API:", response.data);
                setLoans(response.data.emprestimos || []);
                setIsLoading(false);

                const decisionsInit = {};
                response.data.emprestimos.forEach((loan, index) => {
                    
                    const savedDecision = localStorage.getItem(`decision-${index}`);
                    decisionsInit[index] = savedDecision || ""; 
                });
                setLoanDecisions(decisionsInit);
            } catch (err) {
                console.error("Erro na chamada da API:", err.response?.data || err.message);
                setError(err.response?.data?.message || "Erro ao carregar os empréstimos dos clientes.");
            }
        };

        fetchLoanStatus();
    }, []);

    const handleDecisionChange = (index, decision) => {
        // Atualiza a decisão no estado de loanDecisions
        setLoanDecisions(prev => ({
            ...prev,
            [index]: decision
        }));
        
        // atualizar o estado do empréstimo com base na decisão
        setLoans(prevLoans => {
            return prevLoans.map((loan, i) => {
                if (i === index) {
                    let updatedLoan = { ...loan };
                    
                    // atualizar o estado do empréstimo conforme a decisão
                    if (decision === "approve") {
                        updatedLoan.estado = "Aprovado";
                    } else if (decision === "interview") {
                        updatedLoan.estado = "Pendente";
                    } else if (decision === "reject") {
                        updatedLoan.estado = "Rejeitado";
                    }
                    
                    return updatedLoan;
                }
                return loan;
            });
        });

        // armazenamos o estado da decisão no LocalStorage
        localStorage.setItem(`decision-${index}`, decision);
    };

    return (
        <div>
            <h1>Estado dos Empréstimos dos Clientes</h1>
            {error ? (
                <div>
                    <p style={{ color: "red" }}>{error}</p>
                </div>
            ) : isLoading ? (
                <p>A carregar os empréstimos...</p>
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
                                boxShadow: "0 2px 5px rgba(176, 222, 235, 0.1)",
                            }}
                        >
                            <p><strong>Cliente:</strong> {loan.cliente}
                               <span style={{ marginLeft: '20px' }}><strong>Profissão:</strong> {loan.profissao}</span>
                               <span style={{ marginLeft: '20px' }}><strong>Salário:</strong> {loan.salario}</span>
                            </p>
                            <p><strong>Tipo de empréstimo:</strong> {loan.tiposempr}</p>
                            <p><strong>Valor:</strong> {loan.valor}</p>
                            <p><strong>Duração:</strong> {loan.duracao}</p>
                            <p><strong>Estado:</strong> {loan.estado}</p>
                            <div>
                                <label>
                                <strong>Decisão:</strong>
                                    <input
                                        type="radio"
                                        name={`decision-${index}`}
                                        checked={loanDecisions[index] === 'interview'}
                                        onChange={() => handleDecisionChange(index, 'interview')}
                                    />
                                    <strong>Entrevista</strong>
                                </label>
                                <label>
                                    <input
                                        type="radio"
                                        name={`decision-${index}`}
                                        checked={loanDecisions[index] === 'approve'}
                                        onChange={() => handleDecisionChange(index, 'approve')}
                                    />
                                    <strong>Aprovar</strong>
                                </label>
                                <label>
                                    <input
                                        type="radio"
                                        name={`decision-${index}`}
                                        checked={loanDecisions[index] === 'reject'}
                                        onChange={() => handleDecisionChange(index, 'reject')}
                                    />
                                    <strong>Rejeitar</strong>
                                </label>
                            </div>
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
