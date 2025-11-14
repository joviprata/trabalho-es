from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import database as db
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'meuscrum-secret-key-change-in-production'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_cpf' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def dict_to_json(obj):
    """Convert database row objects to dictionaries"""
    if obj is None:
        return None
    if isinstance(obj, list):
        return dict(obj)
    return dict(obj)

@app.route('/')
def index():
    if 'user_cpf' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        senha = data.get('senha')
        
        user = db.authenticate_user(email, senha)
        if user:
            session['user_cpf'] = user['cpf']
            session['user_nome'] = user['nome']
            session['user_email'] = user['email']
            return jsonify({'success': True, 'user': dict_to_json(user)})
        else:
            return jsonify({'success': False, 'message': 'Email ou senha incorretos'}), 401
    
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    cpf = data.get('cpf')
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    
    # Check if user already exists
    if db.get_user(cpf) or db.get_user_by_email(email):
        return jsonify({'success': False, 'message': 'Usuário já existe'}), 400
    
    try:
        db.criar_usuario(cpf, nome, email, senha)
        user = db.get_user(cpf)
        session['user_cpf'] = user['cpf']
        session['user_nome'] = user['nome']
        session['user_email'] = user['email']
        return jsonify({'success': True, 'user': dict_to_json(user)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/api/projetos')
@login_required
def api_projetos():
    projetos = db.get_projetos_usuario(session['user_cpf'])
    if projetos:
        projetos_dict = [dict_to_json(proj) for proj in projetos]
    else:
        projetos_dict = []
    return jsonify({'projetos': projetos_dict})

@app.route('/api/projeto/<int:proj_id>')
@login_required
def api_projeto(proj_id):
    projeto = db.get_projeto(proj_id)
    if projeto:
        backlog = db.get_backlogprod_by_projeto(proj_id)
        sprints = db.get_sprints_by_projeto(proj_id)
        usuarios = db.get_usuarios_projeto(proj_id)
        if sprints:
            sprints_dict = [dict_to_json(sprint) for sprint in sprints]
        else:
            sprints_dict = [] 
        if usuarios:
            usuarios_dict = [dict_to_json(usr) for usr in usuarios]
        else:
            usuarios_dict = []
        # Determine current user's papel in this projeto (if any)
        user_papel = None
        try:
            for u in usuarios:
                # u contains fields from tb_usuario plus Papel
                if u.get('cpf') == session.get('user_cpf') or u.get('CPF') == session.get('user_cpf'):
                    # Papel may be present in the join as 'papel' or 'Papel'
                    user_papel = u.get('papel') or u.get('Papel')
                    break
        except Exception:
            user_papel = None
        return jsonify({
            'projeto': dict_to_json(projeto),
            'backlog': dict_to_json(backlog),
            'sprints': sprints_dict,
            'usuarios': usuarios_dict,
            'user_papel': user_papel
        })
    return jsonify({'error': 'Projeto não encontrado'}), 404

@app.route('/api/projeto', methods=['POST'])
@login_required
def api_criar_projeto():
    data = request.get_json()
    nome = data.get('nome')
    datafim = data.get('datafim')
    status = data.get('status', 'Em Andamento')
    
    try:
        proj_id = db.criar_projeto(nome, datafim, status)
        if not proj_id:
            return jsonify({'success': False, 'message': 'Erro ao criar projeto'}), 500
        # Add creator to project
        db.integrar_usuario_projeto(proj_id, session['user_cpf'], 'ProductOwner')
        projeto = db.get_projeto(proj_id)
        # Create backlog for project
        db.criar_backlogProduto(proj_id, f"Backlog do Produto - {nome}")
        return jsonify({'success': True, 'projeto': dict_to_json(projeto)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/projeto/<int:proj_id>', methods=['PUT'])
@login_required
def api_atualizar_projeto(proj_id):
    data = request.get_json()
    if 'datafim' in data:
        db.update_datafim_projeto(proj_id, data['datafim'])
    if 'status' in data:
        db.update_projeto_status(proj_id, data['status'])
    projeto = db.get_projeto(proj_id)
    return jsonify({'success': True, 'projeto': dict_to_json(projeto)})

@app.route('/api/backlog/<int:bp_id>/userstories')
@login_required
def api_userstories(bp_id):
    userstories = db.get_backlogprod_userstories(bp_id)
    if userstories:
        userstories_dict = [dict_to_json(usr) for usr in userstories]
    else:
        userstories_dict = []  
    return jsonify({'userstories': userstories_dict})

@app.route('/api/userstory/<int:us_id>')
@login_required
def api_userstory(us_id):
    userstory = db.get_userstory(us_id)
    return jsonify({'userstory': dict_to_json(userstory)})

@app.route('/api/userstory', methods=['POST'])
@login_required
def api_criar_userstory():
    data = request.get_json()
    backlogprod = data.get('backlogprod')
    titulo = data.get('titulo')
    desc = data.get('descricao')
    prioridade = data.get('prioridade', 'Média')
    status = data.get('status', 'A fazer')
    
    # Check if user is ProductOwner
    try:
        bp = db.get_backlogprod(backlogprod)
        if bp:
            proj_id = bp.get('projeto') or bp.get('Projeto')
            if proj_id:
                usuarios = db.get_usuarios_projeto(proj_id)
                is_product_owner = False
                if usuarios:
                    for u in usuarios:
                        if u.get('cpf') == session.get('user_cpf') or u.get('CPF') == session.get('user_cpf'):
                            papel = u.get('papel') or u.get('Papel')
                            if papel == 'ProductOwner' or papel == 'Product Owner':
                                is_product_owner = True
                            break
                if not is_product_owner:
                    return jsonify({'success': False, 'message': 'Apenas o Product Owner pode criar user stories'}), 403
    except Exception as e:
        return jsonify({'success': False, 'message': 'Erro ao verificar permissões'}), 403
    
    try:
        us_id = db.criar_userStory(backlogprod, session['user_cpf'], titulo, desc, prioridade, status)
        userstory = db.get_userstory(us_id)
        return jsonify({'success': True, 'userstory': dict_to_json(userstory)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/userstory/<int:us_id>', methods=['PUT'])
@login_required
def api_atualizar_userstory(us_id):
    data = request.get_json()
    
    # Check if user is ProductOwner
    try:
        userstory = db.get_userstory(us_id)
        if userstory:
            backlogprod = userstory.get('backlogprod') or userstory.get('BacklogProd')
            if backlogprod:
                bp = db.get_backlogprod(backlogprod)
                if bp:
                    proj_id = bp.get('projeto') or bp.get('Projeto')
                    if proj_id:
                        usuarios = db.get_usuarios_projeto(proj_id)
                        is_product_owner = False
                        if usuarios:
                            for u in usuarios:
                                if u.get('cpf') == session.get('user_cpf') or u.get('CPF') == session.get('user_cpf'):
                                    papel = u.get('papel') or u.get('Papel')
                                    if papel == 'ProductOwner' or papel == 'Product Owner':
                                        is_product_owner = True
                                    break
                        if not is_product_owner:
                            return jsonify({'success': False, 'message': 'Apenas o Product Owner pode editar user stories'}), 403
    except Exception as e:
        return jsonify({'success': False, 'message': 'Erro ao verificar permissões'}), 403
    
    if 'prioridade' in data:
        db.update_userstory_prioridade(us_id, data['prioridade'])
    if 'status' in data:
        db.update_userstory_status(us_id, data['status'])
    if 'titulo' in data:
        db.update_userstory_titulo(us_id, data['titulo'])
    if 'descricao' in data:
        db.update_userstory_descricao(us_id, data['descricao'])
    if 'responsavel' in data:
        db.add_responsavel2userstory(us_id, data['responsavel'])
    if 'backlogsprint' in data:
        db.add_userstory2backlogsprint(us_id, data['backlogsprint'])
    userstory = db.get_userstory(us_id)
    return jsonify({'success': True, 'userstory': dict_to_json(userstory)})

@app.route('/api/userstory/<int:us_id>', methods=['DELETE'])
@login_required
def api_deletar_userstory(us_id):
    db.delete_userstory(us_id)
    return jsonify({'success': True})

@app.route('/api/sprint', methods=['POST'])
@login_required
def api_criar_sprint():
    data = request.get_json()
    projeto = data.get('projeto')
    titulo = data.get('titulo')
    datainicio = data.get('datainicio')
    datafim = data.get('datafim')
    status = data.get('status', 'Planejada')
    
    # Check if user is ScrumMaster
    try:
        usuarios = db.get_usuarios_projeto(projeto)
        is_scrum_master = False
        if usuarios:
            for u in usuarios:
                if u.get('cpf') == session.get('user_cpf') or u.get('CPF') == session.get('user_cpf'):
                    papel = u.get('papel') or u.get('Papel')
                    if papel == 'ScrumMaster' or papel == 'Scrum Master':
                        is_scrum_master = True
                    break
        if not is_scrum_master:
            return jsonify({'success': False, 'message': 'Apenas o Scrum Master pode criar sprints'}), 403
    except Exception as e:
        return jsonify({'success': False, 'message': 'Erro ao verificar permissões'}), 403
    
    try:
        sprint_id = db.criar_sprint(projeto, titulo, datainicio, datafim, status)
        # Create backlog for sprint
        db.criar_backlogSprint(sprint_id)
        # Create empty plano-sprint for sprint
        db.criar_planoSprint(sprint_id, '', '', '', '')
        sprint = db.get_sprint(sprint_id)
        return jsonify({'success': True, 'sprint': dict_to_json(sprint)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sprint/<int:sprint_id>')
@login_required
def api_sprint(sprint_id):
    sprint = db.get_sprint(sprint_id)
    if sprint:
        backlog = db.get_backlogsprint_by_sprint(sprint_id)
        plano = db.get_planosprint_by_sprint(sprint_id)
        if backlog:
            userstories = db.get_backlogsprint_userstories(backlog['bs_id'])
        else:
            userstories = []
        if userstories:
            userstories_dict = [dict_to_json(usr) for usr in userstories]
        else:
            userstories_dict = []
        tarefas = []  
        if tarefas:
            tarefas_dict = [dict_to_json(tarefa) for tarefa in tarefas]
        else:
            tarefas_dict = [] 
        if plano:
            tarefas = db.get_tarefas(plano['ps_id'])
        return jsonify({
            'sprint': dict_to_json(sprint),
            'backlog': dict_to_json(backlog),
            'plano': dict_to_json(plano),
            'userstories': userstories_dict,
            'tarefas': tarefas_dict
        })
    return jsonify({'error': 'Sprint não encontrada'}), 404

@app.route('/api/sprint/<int:sprint_id>', methods=['PUT'])
@login_required
def api_atualizar_sprint(sprint_id):
    data = request.get_json()
    
    # Check if user is ScrumMaster
    try:
        sprint_data = db.get_sprint(sprint_id)
        if sprint_data:
            proj_id = sprint_data.get('projeto') or sprint_data.get('Projeto')
            if proj_id:
                usuarios = db.get_usuarios_projeto(proj_id)
                is_scrum_master = False
                if usuarios:
                    for u in usuarios:
                        if u.get('cpf') == session.get('user_cpf') or u.get('CPF') == session.get('user_cpf'):
                            papel = u.get('papel') or u.get('Papel')
                            if papel == 'ScrumMaster' or papel == 'Scrum Master':
                                is_scrum_master = True
                            break
                if not is_scrum_master:
                    return jsonify({'success': False, 'message': 'Apenas o Scrum Master pode alterar sprints'}), 403
    except Exception as e:
        return jsonify({'success': False, 'message': 'Erro ao verificar permissões'}), 403
    
    if 'status' in data:
        db.update_sprint_status(sprint_id, data['status'])
    if 'titulo' in data:
        db.update_sprint_title(sprint_id, data['titulo'])
    sprint = db.get_sprint(sprint_id)
    return jsonify({'success': True, 'sprint': dict_to_json(sprint)})


@app.route('/api/projeto/<int:proj_id>/role', methods=['PUT'])
@login_required
def api_update_projeto_role(proj_id):
    """Atualiza o papel do usuário logado no projeto."""
    data = request.get_json()
    papel = data.get('papel')
    valid = ['ProductOwner', 'ScrumMaster', 'Developer', 'Product Owner', 'Scrum Master']
    if papel is None:
        return jsonify({'success': False, 'message': 'Papel não informado'}), 400
    # Normalize common labels
    if papel == 'Product Owner':
        papel = 'ProductOwner'
    if papel == 'Scrum Master':
        papel = 'ScrumMaster'
    if papel not in ['ProductOwner', 'ScrumMaster', 'Developer']:
        return jsonify({'success': False, 'message': 'Papel inválido'}), 400
    try:
        db.update_papel_userproj(proj_id, session['user_cpf'], papel)
        return jsonify({'success': True, 'papel': papel})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/sprint/<int:sprint_id>/userstory', methods=['POST'])
@login_required
def api_add_userstory_to_sprint(sprint_id):
    """Adiciona uma user story ao backlog da sprint (usa BacklogSprint = bs_id)."""
    data = request.get_json()
    us_id = data.get('userstory') or data.get('us_id') or data.get('userstory_id')
    if not us_id:
        return jsonify({'success': False, 'message': 'User story não informada'}), 400
    backlog = db.get_backlogsprint_by_sprint(sprint_id)
    if not backlog:
        return jsonify({'success': False, 'message': 'Backlog da sprint não encontrado'}), 404
    try:
        db.add_userstory2backlogsprint(us_id, backlog['bs_id'])
        userstories = db.get_backlogsprint_userstories(backlog['bs_id'])
        if userstories:
            userstories_dict = [dict_to_json(us) for us in userstories]
        else:
            userstories_dict = []
        return jsonify({'success': True, 'userstories': userstories_dict})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/sprint/<int:sprint_id>/userstory/<int:us_id>', methods=['DELETE'])
@login_required
def api_remove_userstory_from_sprint(sprint_id, us_id):
    """Remove a associação da user story com o backlog da sprint (BacklogSprint = NULL)."""
    backlog = db.get_backlogsprint_by_sprint(sprint_id)
    if not backlog:
        return jsonify({'success': False, 'message': 'Backlog da sprint não encontrado'}), 404
    try:
        db.remove_userstory_from_backlogsprint(us_id)
        userstories = db.get_backlogsprint_userstories(backlog['bs_id'])
        if userstories:
            userstories_dict = [dict_to_json(us) for us in userstories]
        else:
            userstories_dict = []
        return jsonify({'success': True, 'userstories': userstories_dict})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/plano-sprint', methods=['POST'])
@login_required
def api_criar_plano_sprint():
    data = request.get_json()
    sprint = data.get('sprint')
    objetivo = data.get('objetivo', '')
    trabalho = data.get('trabalho', '')
    equipe = data.get('equipe', '')
    saida = data.get('saida', '')
    
    try:
        ps_id = db.criar_planoSprint(sprint, objetivo, trabalho, equipe, saida)
        plano = db.get_planosprint(ps_id)
        return jsonify({'success': True, 'plano': dict_to_json(plano)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/planosprint/<int:ps_id>')
@login_required
def api_get_planosprint(ps_id):
    plano = db.get_planosprint(ps_id)
    if plano:
        tarefas = db.get_tarefas(ps_id)
        if tarefas:
            tarefas_dict = [dict_to_json(tarefa) for tarefa in tarefas]
        else:
            tarefas_dict = [] 
        return jsonify({
            'plano': dict_to_json(plano),
            'tarefas': tarefas_dict
        })
    return jsonify({'error': 'Plano de sprint não encontrado'}), 404

@app.route('/api/plano-sprint/<int:ps_id>', methods=['PUT'])
@login_required
def api_atualizar_plano_sprint(ps_id):
    data = request.get_json()
    if 'objetivo' in data:
        db.update_sprintplan_objetivo(ps_id, data['objetivo'])
    if 'trabalho' in data:
        db.update_sprintplan_trabalho(ps_id, data['trabalho'])
    if 'equipe' in data:
        db.update_sprintplan_equipe(ps_id, data['equipe'])
    if 'saida' in data:
        db.update_sprintplan_saida(ps_id, data['saida'])
    plano = db.get_planosprint(ps_id)
    return jsonify({'success': True, 'plano': dict_to_json(plano)})

@app.route('/api/tarefa', methods=['POST'])
@login_required
def api_criar_tarefa():
    data = request.get_json()
    planosprint = data.get('planosprint')
    desc = data.get('descricao')
    status = data.get('status', 'A fazer')
    
    try:
        tarefa_id = db.criar_tarefa(planosprint, desc, status)
        # Get tarefa details would require a get_tarefa function
        return jsonify({'success': True, 'tarefa_id': tarefa_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/tarefa/<int:tarefa_id>', methods=['PUT'])
@login_required
def api_atualizar_tarefa(tarefa_id):
    data = request.get_json()
    if 'status' in data:
        db.update_status_tarefa(tarefa_id, data['status'])
    if 'descricao' in data:
        db.update_descricao_tarefa(tarefa_id, data['descricao'])
    if 'responsavel' in data:
        db.add_responsavel2tarefa(tarefa_id, data['responsavel'])
    if 'datafim' in data:
        db.update_datafim_tarefa(tarefa_id, data['datafim'])
    return jsonify({'success': True})

@app.route('/api/tarefa/<int:tarefa_id>', methods=['DELETE'])
@login_required
def api_deletar_tarefa(tarefa_id):
    db.delete_tarefa(tarefa_id)
    return jsonify({'success': True})

@app.route('/api/usuarios')
@login_required
def api_usuarios():
    usuarios = db.get_all_usuarios()
    return jsonify({'usuarios': dict_to_json(usuarios)})

@app.route('/api/usuario/atual')
@login_required
def api_usuario_atual():
    user = db.get_user(session['user_cpf'])
    return jsonify({'user': dict_to_json(user)})

@app.route('/api/usuario/atualizar', methods=['PUT'])
@login_required
def api_atualizar_usuario():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    
    db.update_user(session['user_cpf'], nome=nome, email=email, senha=senha)
    user = db.get_user(session['user_cpf'])
    session['user_nome'] = user['nome']
    session['user_email'] = user['email']
    return jsonify({'success': True, 'user': dict_to_json(user)})

@app.route('/projeto/<int:proj_id>')
@login_required
def projeto(proj_id):
    return render_template('projeto.html', proj_id=proj_id)

@app.route('/backlog/<int:bp_id>')
@login_required
def backlog(bp_id):
    # Get backlog to get the project and determine user's role
    bp = db.get_backlogprod(bp_id)
    user_papel = None
    if bp:
        proj_id = bp.get('projeto') or bp.get('Projeto')
        if proj_id:
            usuarios = db.get_usuarios_projeto(proj_id)
            if usuarios:
                for u in usuarios:
                    if u.get('cpf') == session.get('user_cpf') or u.get('CPF') == session.get('user_cpf'):
                        user_papel = u.get('papel') or u.get('Papel')
                        break
    return render_template('backlog.html', bp_id=bp_id, user_papel=user_papel)

@app.route('/sprint/<int:sprint_id>')
@login_required
def sprint(sprint_id):
    # Get sprint to get the project and determine user's role
    sprint_data = db.get_sprint(sprint_id)
    user_papel = None
    if sprint_data:
        proj_id = sprint_data.get('projeto') or sprint_data.get('Projeto')
        if proj_id:
            usuarios = db.get_usuarios_projeto(proj_id)
            if usuarios:
                for u in usuarios:
                    if u.get('cpf') == session.get('user_cpf') or u.get('CPF') == session.get('user_cpf'):
                        user_papel = u.get('papel') or u.get('Papel')
                        break
    return render_template('sprint.html', sprint_id=sprint_id, user_papel=user_papel)

@app.route('/plano-sprint/<int:ps_id>')
@login_required
def plano_sprint(ps_id):
    # Get plano-sprint to get the sprint and project and determine user's role
    plano_data = db.get_planosprint(ps_id)
    user_papel = None
    if plano_data:
        sprint_id = plano_data.get('sprint') or plano_data.get('Sprint')
        if sprint_id:
            sprint_data = db.get_sprint(sprint_id)
            if sprint_data:
                proj_id = sprint_data.get('projeto') or sprint_data.get('Projeto')
                if proj_id:
                    usuarios = db.get_usuarios_projeto(proj_id)
                    if usuarios:
                        for u in usuarios:
                            if u.get('cpf') == session.get('user_cpf') or u.get('CPF') == session.get('user_cpf'):
                                user_papel = u.get('papel') or u.get('Papel')
                                break
    return render_template('plano-sprint.html', ps_id=ps_id, user_papel=user_papel)

@app.route('/configuracoes')
@login_required
def configuracoes():
    return render_template('configuracoes.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

