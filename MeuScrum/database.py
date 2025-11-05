import psycopg2
import psycopg2.extras #Esse modulo permite a gente obter um dicionario quando fazemos um select,
#dai ao inves de precisarmos saber qual a posicao da coluna na lista, podemos so fazer
#"nome_variavel"["name"], embaixo, dentro do try, tem um exemplo.

def comandoSQL(comando):
    hostname = 'localhost'
    database = 'BDMeuScrum'
    username = 'postgres'
    pwd = 'admin'
    port_id = 5432
    conn = None
    cur = None

    try:
        conn = psycopg2.connect(
            host = hostname,
            dbname = database,
            user = username,
            password = pwd,
            port = port_id
        )
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        #Tratamendo dos comandos SQL
        cur.execute(comando)
        if comando[:3].lower() == "sel":
            return cur.fetchall()
        elif comando.strip().lower().startswith(("update", "insert", "delete", "call")):
            if "returning" in comando.lower():
                result = cur.fetchone()
                conn.commit()
                return result
            else:
                conn.commit()
                return None

    except Exception as error:
        raise Exception(error)
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

# Insere email na tabela de email de pessoas
def criar_usuario(cpf,nome,email,senha):
    comandoSQL(f"""INSERT INTO tb_usuario (CPF, Nome, Email, Senha, DataCriacao) VALUES 
               ('{cpf}', '{nome}', '{email}', '{senha}', CURRENT_DATE)""")
    return

def criar_projeto(nome,datafim,status):
    comandoSQL(f"""INSERT INTO tb_projeto (Nome, DataInicio, DataFim, Status) VALUES 
               ('{nome}', CURRENT_DATE, {'NULL' if datafim is None else f"'{datafim}'"}, '{status}')""")
    return

def integrar_usuario_projeto(projeto, usuario, papel):
    comandoSQL(f"""INSERT INTO tb_userproj (Projeto, Usuario, Papel, DataEntrada) VALUES 
               ('{projeto}', '{usuario}', '{papel}', CURRENT_DATE)""")
    return

def criar_backlogProduto(projeto, titulo):
    comandoSQL(f"""INSERT INTO tb_backlogproduto (Projeto, Titulo, DataCriado) VALUES 
               ('{projeto}', '{titulo}', CURRENT_DATE)""")
    return

def criar_userStory(backlogprod,criador,titulo,desc,prioridade,status):
    comandoSQL(f"""INSERT INTO tb_userstory (BacklogProd, CriadoPor, Titulo, Descricao, Prioridade, Status, DataCriado) VALUES 
               ('{backlogprod}', '{criador}', '{titulo}', '{desc}', '{prioridade}', '{status}', CURRENT_DATE)""")
    return

def criar_sprint(projeto, titulo, datainicio, datafim, status):
    comandoSQL(f"""INSERT INTO tb_sprint (Projeto, Titulo, DataInicio, DataFim, Status) VALUES 
               ('{projeto}', '{titulo}', '{datainicio}', '{datafim}', '{status}')""")
    return

def criar_backlogSprint(sprint):
    comandoSQL(f"""INSERT INTO tb_backlogsprint (Sprint) VALUES 
               ('{sprint}')""")
    return

def criar_planoSprint(sprint, objetivo, trabalho, equipe, saida):
    comandoSQL(f"""INSERT INTO tb_planosprint (Sprint, Objetivo, Trabalho, Equipe, Saida) VALUES 
               ('{sprint}', '{objetivo}', '{trabalho}', '{equipe}', '{saida}')""")
    return

def criar_tarefa(planoSprint, desc, status):
    comandoSQL(f"""INSERT INTO tb_tarefa (PlanoSprint, Descricao, Status, DataCriacao) VALUES 
               ('{planoSprint}', '{desc}', '{status}', CURRENT_DATE)""")
    return

def update_datafim_projeto(id,datafim):
    comandoSQL(f"UPDATE tb_projeto SET DataFim = '{datafim}' WHERE Proj_id = '{id}'")
    return

def update_datasaida_userproj(projeto,usuario,datasaida):
    comandoSQL(f"UPDATE tb_userproj SET DataSaida = '{datasaida}' WHERE Projeto = '{projeto}' and Usuario = '{usuario}")
    return

def update_papel_userproj(projeto,usuario,papel):
    comandoSQL(f"UPDATE tb_userproj SET Papel = '{papel}' WHERE Projeto = '{projeto}' and Usuario = '{usuario}")
    return

def add_userstory2backlogsprint(userstory,backlogsprint):
    comandoSQL(f"UPDATE tb_userstory SET BacklogSprint = '{backlogsprint}' WHERE US_id = '{userstory}'")
    return

def add_responsavel2userstory(userstory,responsavel):
    comandoSQL(f"UPDATE tb_userstory SET Responsavel = '{responsavel}' WHERE US_id = '{userstory}'")
    return

def update_userstory_prioridade(userstory,prioridade):
    comandoSQL(f"UPDATE tb_userstory SET Prioridade = '{prioridade}' WHERE US_id = '{userstory}'")
    return

def update_userstory_status(userstory,status):
    comandoSQL(f"UPDATE tb_userstory SET Status = '{status}' WHERE US_id = '{userstory}'")
    return

def update_sprint_status(sprint,status):
    comandoSQL(f"UPDATE tb_sprint SET Status = '{status}' WHERE Sprint_id = '{sprint}'")
    return

def update_sprint_title(sprint,title):
    comandoSQL(f"UPDATE tb_sprint SET Titulo = '{title}' WHERE Sprint_id = '{sprint}'")
    return

def update_sprintplan_objetivo(sprintplan,objetivo):
    comandoSQL(f"UPDATE tb_PlanoSprint SET Objetivo = '{objetivo}' WHERE PS_id = '{sprintplan}'")
    return

def update_sprintplan_trabalho(sprintplan,trabalho):
    comandoSQL(f"UPDATE tb_PlanoSprint SET Trabalho = '{trabalho}' WHERE PS_id = '{sprintplan}'")
    return

def update_sprintplan_equipe(sprintplan,equipe):
    comandoSQL(f"UPDATE tb_PlanoSprint SET Equipe = '{equipe}' WHERE PS_id = '{sprintplan}'")
    return

def update_sprintplan_saida(sprintplan,saida):
    comandoSQL(f"UPDATE tb_PlanoSprint SET Saida = '{saida}' WHERE PS_id = '{sprintplan}'")
    return

def add_responsavel2tarefa(tarefa,responsavel):
    comandoSQL(f"UPDATE tb_Tarefa SET Responsavel = '{responsavel}' WHERE Tarefa_id = '{tarefa}'")
    return

def update_descricao_tarefa(tarefa,desc):
    comandoSQL(f"UPDATE tb_Tarefa SET Descricao = '{desc}' WHERE Tarefa_id = '{tarefa}'")
    return

def update_status_tarefa(tarefa,status):
    comandoSQL(f"UPDATE tb_Tarefa SET Status = '{status}' WHERE Tarefa_id = '{tarefa}'")
    return

def update_datafim_tarefa(tarefa,datafim):
    comandoSQL(f"UPDATE tb_Tarefa SET DataFim = '{datafim}' WHERE Tarefa_id = '{tarefa}'")
    return

def get_user(cpf):
    return comandoSQL(f"SELECT * FROM tb_usuario WHERE CPF = '{cpf}'")

def get_projeto(id):
    return comandoSQL(f"SELECT * FROM tb_projeto WHERE Proj_id = '{id}'")

def get_backlogprod(id):
    return comandoSQL(f"SELECT * FROM tb_backlogproduto WHERE BP_id = '{id}'")

def get_sprint(id):
    return comandoSQL(f"SELECT * FROM tb_sprint WHERE Sprint_id = '{id}'")

def get_backlogsprint(id):
    return comandoSQL(f"SELECT * FROM tb_backlogsprint WHERE BS_id = '{id}'")

def get_planosprint(id):
    return comandoSQL(f"SELECT * FROM tb_planosprint WHERE PS_id = '{id}'")

def get_tarefas(planosprint):
    return comandoSQL(f"SELECT * FROM tb_tarefa WHERE planosprint = '{planosprint}'")

def get_backlogprod_userstories(bp_id):
    return comandoSQL(f"SELECT * FROM tb_userstory WHERE backlogprod = '{bp_id}'")

def get_backlogsprint_userstories(bs_id):
    return comandoSQL(f"SELECT * FROM tb_userstory WHERE backlogsprint = '{bs_id}'")

def get_userstory(id):
    return comandoSQL(f"SELECT * FROM tb_userstory WHERE US_id = '{id}'")

def delete_userstory(id):
    comandoSQL(f"DELETE FROM tb_pessoa WHERE cpf = '{id}'")
    return

def delete_backlogprod(id):
    comandoSQL(f"DELETE FROM tb_backlogproduto WHERE BP_id = '{id}'")
    return

def delete_backlogsprint(id):
    comandoSQL(f"DELETE FROM tb_backlogsprint WHERE BS_id = '{id}'")
    return

def delete_planoprint(id):
    comandoSQL(f"DELETE FROM tb_planosprint WHERE PS_id = '{id}'")
    return
