CREATE TYPE Tipo_Papel AS ENUM('ProductOwner','ScrumMaster','Developer');

CREATE TABLE TB_Usuario(
	CPF char(11) PRIMARY KEY,
	Nome varchar(255) NOT NULL,
	Email varchar(255) UNIQUE NOT NULL,
	Senha varchar(30) NOT NULL,
	DataCriacao DATE NOT NULL
);

CREATE TABLE TB_Projeto(
	Proj_id SERIAL PRIMARY KEY,
	Nome varchar(255) NOT NULL,
	DataInicio DATE NOT NULL,
	DataFim DATE,
	Status varchar(50) NOT NULL
);

CREATE TABLE TB_UserProj(
	Projeto SERIAL NOT NULL,
	Usuario char(11) NOT NULL,
	Papel Tipo_Papel NOT NULL,
	DataEntrada DATE NOT NULL,
	DataSaida DATE,
	PRIMARY KEY(Projeto,Usuario)
);

CREATE TABLE TB_BacklogProduto(
	BP_id SERIAL PRIMARY KEY,
	Projeto SERIAL NOT NULL,
	Titulo varchar(255) NOT NULL,
	DataCriado DATE NOT NULL
);

CREATE TABLE TB_UserStory(
	US_id SERIAL PRIMARY KEY,
	BacklogProd SERIAL NOT NULL,
	BacklogSprint SERIAL,
	Responsavel char(11),
	CriadoPor char(11) NOT NULL,
	Titulo varchar(255) NOT NULL,
	Descricao text NOT NULL,
	Prioridade varchar(20) NOT NULL,
	Status varchar(30) NOT NULL,
	DataCriado DATE NOT NULL
);

CREATE TABLE TB_Sprint(
	Sprint_id SERIAL PRIMARY KEY,
	Projeto SERIAL NOT NULL,
	Titulo varchar(100) NOT NULL,
	DataInicio DATE NOT NULL,
	DataFim DATE NOT NULL,
	Status varchar(30) NOT NULL
);

CREATE TABLE TB_BacklogSprint(
	BS_id SERIAL PRIMARY KEY,
	Sprint SERIAL NOT NULL
);

CREATE TABLE TB_PlanoSprint(
	PS_id SERIAL PRIMARY KEY,
	Sprint SERIAL NOT NULL,
	Objetivo TEXT,
	Trabalho TEXT,
	Equipe TEXT,
	Saida TEXT
);

CREATE TABLE TB_Tarefa(
	Tarefa_id SERIAL PRIMARY KEY,
	PlanoSprint SERIAL NOT NULL,
	Responsavel char(11),
	Descricao text,
	Status varchar(30),
	DataCriacao DATE NOT NULL,
	DataFim DATE
);

ALTER TABLE TB_UserProj
ADD FOREIGN KEY(Projeto)
REFERENCES TB_Projeto(Proj_id);

ALTER TABLE TB_UserProj
ADD FOREIGN KEY(Usuario)
REFERENCES TB_Usuario(CPF);

ALTER TABLE TB_BacklogProduto
ADD FOREIGN KEY(Projeto)
REFERENCES TB_Projeto(Proj_id);

ALTER TABLE TB_UserStory
ADD FOREIGN KEY(BacklogProd)
REFERENCES TB_BacklogProduto(BP_id);

ALTER TABLE TB_UserStory
ADD FOREIGN KEY(BacklogSprint)
REFERENCES TB_BacklogSprint(BS_id);

ALTER TABLE TB_UserStory
ADD FOREIGN KEY(Responsavel)
REFERENCES TB_Usuario(CPF);

ALTER TABLE TB_UserStory
ADD FOREIGN KEY(CriadoPor)
REFERENCES TB_Usuario(CPF);

ALTER TABLE TB_Sprint
ADD FOREIGN KEY(Projeto)
REFERENCES TB_Projeto(Proj_id);

ALTER TABLE TB_BacklogSprint
ADD FOREIGN KEY(Sprint)
REFERENCES TB_Sprint(Sprint_id);

ALTER TABLE TB_PlanoSprint
ADD FOREIGN KEY(Sprint)
REFERENCES TB_Sprint(Sprint_id);

ALTER TABLE TB_Tarefa
ADD FOREIGN KEY(Responsavel)
REFERENCES TB_Usuario(CPF);

ALTER TABLE TB_Tarefa
ADD FOREIGN KEY(PlanoSprint)
REFERENCES TB_PlanoSprint(PS_id);