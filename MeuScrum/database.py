import psycopg2
import psycopg2.extras #Esse modulo permite a gente obter um dicionario quando fazemos um select,
#dai ao inves de precisarmos saber qual a posicao da coluna na lista, podemos so fazer
#"nome_variavel"["name"], embaixo, dentro do try, tem um exemplo.

def comandoSQL(comando, params=None):
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
        if params:
            cur.execute(comando, params)
        else:
            cur.execute(comando)
        if comando[:3].lower() == "sel" or comando.strip().lower().startswith("select"):
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
    comandoSQL("""INSERT INTO tb_usuario (CPF, Nome, Email, Senha, DataCriacao) VALUES 
               (%s, %s, %s, %s, CURRENT_DATE)""", (cpf, nome, email, senha))
    return

def criar_projeto(nome,datafim,status):
    if datafim:
        result = comandoSQL("""INSERT INTO tb_projeto (Nome, DataInicio, DataFim, Status) VALUES 
                   (%s, CURRENT_DATE, %s, %s) RETURNING Proj_id""", (nome, datafim, status))
    else:
        result = comandoSQL("""INSERT INTO tb_projeto (Nome, DataInicio, DataFim, Status) VALUES 
                   (%s, CURRENT_DATE, NULL, %s) RETURNING Proj_id""", (nome, status))
    return result['proj_id'] if result else None

def integrar_usuario_projeto(projeto, usuario, papel):
    comandoSQL("""INSERT INTO tb_userproj (Projeto, Usuario, Papel, DataEntrada) VALUES 
               (%s, %s, %s, CURRENT_DATE)""", (projeto, usuario, papel))
    return

def criar_backlogProduto(projeto, titulo):
    result = comandoSQL("""INSERT INTO tb_backlogproduto (Projeto, Titulo, DataCriado) VALUES 
               (%s, %s, CURRENT_DATE) RETURNING BP_id""", (projeto, titulo))
    return result['bp_id'] if result else None

def criar_userStory(backlogprod,criador,titulo,desc,prioridade,status):
    result = comandoSQL("""INSERT INTO tb_userstory (BacklogProd, BacklogSprint, CriadoPor, Titulo, Descricao, Prioridade, Status, DataCriado) VALUES 
               (%s, %s, %s, %s, %s, %s, %s, CURRENT_DATE) RETURNING US_id""",
               (backlogprod, None, criador, titulo, desc, prioridade, status))
    return result['us_id'] if result else None

def criar_sprint(projeto, titulo, datainicio, datafim, status):
    result = comandoSQL("""INSERT INTO tb_sprint (Projeto, Titulo, DataInicio, DataFim, Status) VALUES 
               (%s, %s, %s, %s, %s) RETURNING Sprint_id""", (projeto, titulo, datainicio, datafim, status))
    return result['sprint_id'] if result else None

def criar_backlogSprint(sprint):
    result = comandoSQL("""INSERT INTO tb_backlogsprint (Sprint) VALUES 
               (%s) RETURNING BS_id""", (sprint,))
    return result['bs_id'] if result else None

def criar_planoSprint(sprint, objetivo, trabalho, equipe, saida):
    result = comandoSQL("""INSERT INTO tb_planosprint (Sprint, Objetivo, Trabalho, Equipe, Saida) VALUES 
               (%s, %s, %s, %s, %s) RETURNING PS_id""", (sprint, objetivo, trabalho, equipe, saida))
    return result['ps_id'] if result else None

def criar_tarefa(planoSprint, desc, status):
    result = comandoSQL("""INSERT INTO tb_tarefa (PlanoSprint, Descricao, Status, DataCriacao) VALUES 
               (%s, %s, %s, CURRENT_DATE) RETURNING Tarefa_id""", (planoSprint, desc, status))
    return result['tarefa_id'] if result else None

def update_datafim_projeto(id,datafim):
    comandoSQL("UPDATE tb_projeto SET DataFim = %s WHERE Proj_id = %s", (datafim, id))
    return

def update_datasaida_userproj(projeto,usuario,datasaida):
    comandoSQL("UPDATE tb_userproj SET DataSaida = %s WHERE Projeto = %s AND Usuario = %s", (datasaida, projeto, usuario))
    return

def update_papel_userproj(projeto,usuario,papel):
    comandoSQL("UPDATE tb_userproj SET Papel = %s WHERE Projeto = %s AND Usuario = %s", (papel, projeto, usuario))
    return

def add_userstory2backlogsprint(userstory,backlogsprint):
    comandoSQL("UPDATE tb_userstory SET BacklogSprint = %s WHERE US_id = %s", (backlogsprint, userstory))
    return

def remove_userstory_from_backlogsprint(userstory):
    """Remove a associação de uma userstory com um backlog de sprint (seta BacklogSprint = NULL)."""
    comandoSQL("UPDATE tb_userstory SET BacklogSprint = NULL WHERE US_id = %s", (userstory,))
    return

def add_responsavel2userstory(userstory,responsavel):
    comandoSQL("UPDATE tb_userstory SET Responsavel = %s WHERE US_id = %s", (responsavel, userstory))
    return

def update_userstory_prioridade(userstory,prioridade):
    comandoSQL("UPDATE tb_userstory SET Prioridade = %s WHERE US_id = %s", (prioridade, userstory))
    return

def update_userstory_status(userstory,status):
    comandoSQL("UPDATE tb_userstory SET Status = %s WHERE US_id = %s", (status, userstory))
    return

def update_userstory_titulo(userstory, titulo):
    comandoSQL("UPDATE tb_userstory SET Titulo = %s WHERE US_id = %s", (titulo, userstory))
    return

def update_userstory_descricao(userstory, descricao):
    comandoSQL("UPDATE tb_userstory SET Descricao = %s WHERE US_id = %s", (descricao, userstory))
    return

def update_sprint_status(sprint,status):
    comandoSQL("UPDATE tb_sprint SET Status = %s WHERE Sprint_id = %s", (status, sprint))
    return

def update_sprint_title(sprint,title):
    comandoSQL("UPDATE tb_sprint SET Titulo = %s WHERE Sprint_id = %s", (title, sprint))
    return

def update_sprintplan_objetivo(sprintplan,objetivo):
    comandoSQL("UPDATE tb_PlanoSprint SET Objetivo = %s WHERE PS_id = %s", (objetivo, sprintplan))
    return

def update_sprintplan_trabalho(sprintplan,trabalho):
    comandoSQL("UPDATE tb_PlanoSprint SET Trabalho = %s WHERE PS_id = %s", (trabalho, sprintplan))
    return

def update_sprintplan_equipe(sprintplan,equipe):
    comandoSQL("UPDATE tb_PlanoSprint SET Equipe = %s WHERE PS_id = %s", (equipe, sprintplan))
    return

def update_sprintplan_saida(sprintplan,saida):
    comandoSQL("UPDATE tb_PlanoSprint SET Saida = %s WHERE PS_id = %s", (saida, sprintplan))
    return

def add_responsavel2tarefa(tarefa,responsavel):
    comandoSQL("UPDATE tb_Tarefa SET Responsavel = %s WHERE Tarefa_id = %s", (responsavel, tarefa))
    return

def update_descricao_tarefa(tarefa,desc):
    comandoSQL("UPDATE tb_Tarefa SET Descricao = %s WHERE Tarefa_id = %s", (desc, tarefa))
    return

def update_status_tarefa(tarefa,status):
    comandoSQL("UPDATE tb_Tarefa SET Status = %s WHERE Tarefa_id = %s", (status, tarefa))
    return

def update_datafim_tarefa(tarefa,datafim):
    comandoSQL("UPDATE tb_Tarefa SET DataFim = %s WHERE Tarefa_id = %s", (datafim, tarefa))
    return

def get_user(cpf):
    result = comandoSQL("SELECT * FROM tb_usuario WHERE CPF = %s", (cpf,))
    return result[0] if result else None

def get_user_by_email(email):
    result = comandoSQL("SELECT * FROM tb_usuario WHERE Email = %s", (email,))
    return result[0] if result else None

def authenticate_user(email, senha):
    result = comandoSQL("SELECT * FROM tb_usuario WHERE Email = %s AND Senha = %s", (email, senha))
    return result[0] if result else None

def update_user(cpf, nome=None, email=None, senha=None):
    updates = []
    params = []
    if nome:
        updates.append("Nome = %s")
        params.append(nome)
    if email:
        updates.append("Email = %s")
        params.append(email)
    if senha:
        updates.append("Senha = %s")
        params.append(senha)
    if updates:
        params.append(cpf)
        comandoSQL(f"UPDATE tb_usuario SET {', '.join(updates)} WHERE CPF = %s", tuple(params))
    return

def get_projeto(id):
    result = comandoSQL("SELECT * FROM tb_projeto WHERE Proj_id = %s", (id,))
    return result[0] if result else None

def get_projetos_usuario(cpf):
    return comandoSQL("""SELECT p.* FROM tb_projeto p 
                         INNER JOIN tb_userproj up ON p.Proj_id = up.Projeto 
                         WHERE up.Usuario = %s AND up.DataSaida IS NULL""", (cpf,))

def get_all_projetos():
    return comandoSQL("SELECT * FROM tb_projeto ORDER BY DataInicio DESC")

def get_backlogprod(id):
    result = comandoSQL("SELECT * FROM tb_backlogproduto WHERE BP_id = %s", (id,))
    return result[0] if result else None

def get_backlogprod_by_projeto(projeto_id):
    result = comandoSQL("SELECT * FROM tb_backlogproduto WHERE Projeto = %s", (projeto_id,))
    return result[0] if result else None

def get_sprint(id):
    result = comandoSQL("SELECT * FROM tb_sprint WHERE Sprint_id = %s", (id,))
    return result[0] if result else None

def get_sprints_by_projeto(projeto_id):
    return comandoSQL("SELECT * FROM tb_sprint WHERE Projeto = %s ORDER BY DataInicio DESC", (projeto_id,))

def get_backlogsprint(id):
    result = comandoSQL("SELECT * FROM tb_backlogsprint WHERE BS_id = %s", (id,))
    return result[0] if result else None

def get_backlogsprint_by_sprint(sprint_id):
    result = comandoSQL("SELECT * FROM tb_backlogsprint WHERE Sprint = %s", (sprint_id,))
    return result[0] if result else None

def get_planosprint(id):
    result = comandoSQL("SELECT * FROM tb_planosprint WHERE PS_id = %s", (id,))
    return result[0] if result else None

def get_planosprint_by_sprint(sprint_id):
    result = comandoSQL("SELECT * FROM tb_planosprint WHERE Sprint = %s", (sprint_id,))
    return result[0] if result else None

def get_tarefas(planosprint):
    return comandoSQL("SELECT * FROM tb_tarefa WHERE planosprint = %s ORDER BY DataCriacao", (planosprint,))

def get_backlogprod_userstories(bp_id):
    return comandoSQL("SELECT * FROM tb_userstory WHERE backlogprod = %s ORDER BY Prioridade DESC, DataCriado", (bp_id,))

def get_backlogsprint_userstories(bs_id):
    return comandoSQL("SELECT * FROM tb_userstory WHERE backlogsprint = %s ORDER BY Prioridade DESC", (bs_id,))

def get_userstory(id):
    result = comandoSQL("SELECT * FROM tb_userstory WHERE US_id = %s", (id,))
    return result[0] if result else None

def get_usuarios_projeto(projeto_id):
    return comandoSQL("""SELECT u.*, up.Papel, up.DataEntrada, up.DataSaida 
                         FROM tb_usuario u 
                         INNER JOIN tb_userproj up ON u.CPF = up.Usuario 
                         WHERE up.Projeto = %s AND up.DataSaida IS NULL""", (projeto_id,))

def get_all_usuarios():
    return comandoSQL("SELECT * FROM tb_usuario ORDER BY Nome")

def delete_userstory(id):
    comandoSQL("DELETE FROM tb_userstory WHERE US_id = %s", (id,))
    return

def delete_backlogprod(id):
    comandoSQL("DELETE FROM tb_backlogproduto WHERE BP_id = %s", (id,))
    return

def delete_backlogsprint(id):
    comandoSQL("DELETE FROM tb_backlogsprint WHERE BS_id = %s", (id,))
    return

def delete_planosprint(id):
    comandoSQL("DELETE FROM tb_planosprint WHERE PS_id = %s", (id,))
    return

def delete_tarefa(id):
    comandoSQL("DELETE FROM tb_tarefa WHERE Tarefa_id = %s", (id,))
    return

def delete_sprint(id):
    comandoSQL("DELETE FROM tb_sprint WHERE Sprint_id = %s", (id,))
    return

def delete_projeto(id):
    comandoSQL("DELETE FROM tb_projeto WHERE Proj_id = %s", (id,))
    return

def update_projeto_status(id, status):
    comandoSQL("UPDATE tb_projeto SET Status = %s WHERE Proj_id = %s", (status, id))
    return
