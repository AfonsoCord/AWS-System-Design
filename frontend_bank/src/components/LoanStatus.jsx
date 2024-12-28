import React, { useEffect, useState } from "react";
import api from "../api";
import { ACCESS_TOKEN } from "../constants";
import "../styles/LoanStatus.css";

function LoanStatus() {
    const [loans, setLoans] = useState([]);
    const [loanDecisions, setLoanDecisions] = useState({});
    const [schedules, setSchedules] = useState([])

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

    
    // guardar a decisão selecionada
    const handleSelectDecision = (index, decision) => {
        setLoanDecisions((prevDecisions) => ({
            ...prevDecisions,
            [index]: decision,
        }));
    };


    // enviar para o backend a decisão, estado e horários em caso de entrevista
    const handleSubmit = async (index, id) => {
        const decision = loanDecisions[index];
        if (!decision) {
            alert("Por favor, selecione uma decisão antes de submeter.");
            return;
        }
        
        if (schedules.length === 0 && decision === "requer entrevista") {
            alert("Por favor, selecione os possíveis horários para a entrevista antes de submeter.");
            return;
        }

        const estado =
            decision === "requer entrevista" ? "pendente" :
            decision === "aprovado" ? "resolvido" :
            "resolvido";

        const token = localStorage.getItem(ACCESS_TOKEN)

        const formData = new FormData();
        formData.append("decisao", decision);
        formData.append("id", id);
        formData.append("estado", estado)

        if (decision !== "requer entrevista") {
            setSchedules([]);
            formData.append("horarios", []);
        } else {
            formData.append("horarios", schedules);
        }

        try {
            const res = await api.post('/decision/', formData, {
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "multipart/form-data",
                },
            });

            window.location.reload();

        } catch (error) {
            console.error(error.message);
            alert(error.response?.data?.message || "Ocorreu um erro.");
        }
    };


    // guardar os horários selecionados
    const handleCheckboxChange = (e) => {
        const { value, checked } = e.target;
        
        if (checked) {
            // adicionar o horário ao array de horários quando selecionar
            setSchedules((prevSchedules) => [...prevSchedules, value]);
        } else {
            // remover o horário do array
            setSchedules((prevSchedules) =>
                prevSchedules.filter((schedule) => schedule !== value)
            );
        }
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
                            <p><strong>Valor:</strong> {loan.valor} €</p>
                            <p><strong>Duração:</strong> {loan.duracao} meses</p>
                            <p><strong>Credit Score:</strong> {loan.creditscore}</p>
                            <br></br>
                            <p><strong>Estado:</strong> {loan.estado}</p>
                            {loan.decisao == null ? (
                                <div>
                                    <label>
                                    <strong>Decisão:</strong>
                                        <input
                                            type="radio"
                                            name={`decision-${index}`}
                                            checked={loanDecisions[index] === 'requer entrevista'}
                                            onChange={() => handleSelectDecision(index, 'requer entrevista')}
                                        />
                                        <strong>Requer entrevista</strong>
                                    </label>
                                    <label>
                                        <input
                                            type="radio"
                                            name={`decision-${index}`}
                                            checked={loanDecisions[index] === 'aprovado'}
                                            onChange={() => handleSelectDecision(index, 'aprovado')}
                                        />
                                        <strong>Aprovar</strong>
                                    </label>
                                    <label>
                                        <input
                                            type="radio"
                                            name={`decision-${index}`}
                                            checked={loanDecisions[index] === 'rejeitado'}
                                            onChange={() => handleSelectDecision(index, 'rejeitado')}
                                        />
                                        <strong>Rejeitar</strong>
                                    </label>
                                    <button
                                        className="form-button"
                                        onClick={() => handleSubmit(index, loan.id)}
                                    >
                                        Submeter Decisão
                                    </button>

                                    {loanDecisions[index] === "requer entrevista" && (
                                    <div>
                                        <br />
                                        <p>Selecione possíveis horários para a entrevista:</p>
                                        <label>
                                            <input 
                                                type="checkbox" 
                                                value="10/01/2025 10:00" 
                                                checked={schedules.includes("10/01/2025 10:00")}
                                                onChange={(e) => handleCheckboxChange(e)}
                                            />
                                            10/01/2025 10:00
                                        </label>
                                        <br />
                                        <label>
                                            <input 
                                                type="checkbox" 
                                                value="10/01/2025 11:00" 
                                                checked={schedules.includes("10/01/2025 11:00")}
                                                onChange={(e) => handleCheckboxChange(e)}
                                            />
                                            10/01/2025 11:00
                                        </label>
                                        <br />
                                        <label>
                                            <input 
                                                type="checkbox" 
                                                value="12/01/2025 11:00" 
                                                checked={schedules.includes("12/01/2025 11:00")}
                                                onChange={(e) => handleCheckboxChange(e)}
                                            />
                                            12/01/2025 11:00
                                        </label>
                                        <br />
                                        <label>
                                            <input 
                                                type="checkbox" 
                                                value="13/01/2025 16:00" 
                                                checked={schedules.includes("13/01/2025 16:00")}
                                                onChange={(e) => handleCheckboxChange(e)}
                                            />
                                            13/01/2025 16:00
                                        </label>
                                    </div>
                                    )}
                                </div>
                                ) : loan.decisao == "requer entrevista" ? (
                                    <div>
                                        <strong>Decisão:</strong> Requer entrevista
                                        <label>
                                            <input
                                                type="radio"
                                                name={`decision-${index}`}
                                                checked={loanDecisions[index] === 'aprovado'}
                                                onChange={() => handleSelectDecision(index, 'aprovado')}
                                            />
                                            <strong>Aprovar</strong>
                                        </label>
                                        <label>
                                            <input
                                                type="radio"
                                                name={`decision-${index}`}
                                                checked={loanDecisions[index] === 'rejeitado'}
                                                onChange={() => handleSelectDecision(index, 'rejeitado')}
                                            />
                                            <strong>Rejeitar</strong>
                                        </label>
                                        <button
                                            className="form-final-button"
                                            onClick={() => handleSubmit(index, loan.id)}
                                        >
                                            Submeter Decisão Final
                                        </button>
                                    </div>
                                ) : (
                                    <p><strong>Decisão:</strong> {loan.decisao}</p>
                                )}
                        </div>
                    ))}
                </div>
            ) : (
                <div>
                    <p>Não existem pedidos de empréstimos disponíveis para exibição.</p>
                </div>
            )}
        </div>
    );
}

export default LoanStatus;
