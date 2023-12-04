import json
import sqlite3
import logging

DATABASE_NAME = './db/jogo_investigacao.db'


class DBHelper:
    def __init__(self):
        self.conn = self.create_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()

    def create_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(DATABASE_NAME)
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            # Considerar lançar a exceção ou retornar None
        return conn

    def close_connection(self):
        if self.conn:
            self.conn.close()

    def save_case_from_json(self, data_json):
        caso_id = self.insert_caso(data_json["caso"], data_json["descricao"])
        self.insert_json_caso(data_json, caso_id)

        # Salvando NPCs e suas relações/opiniões
        npc_ids = {}  # Para armazenar os IDs dos NPCs recém-criados
        npcs = data_json["npcs"]
        for npc in npcs:
            npc_id = self.insert_npc(
                caso_id, npc["nome"], npc["historia"], npc["ocupacao"], npc["personalidade"],
                npc["motivacoes"], npc["honestidade"], npc["habilidadesEspeciais"],
                npc["localizacaoDuranteCrime"], npc["culpado"], npc
            )
            npc_ids[npc["nome"]] = npc_id
        print("NPCS Done")

        for npc in npcs:
            npc_name = npc["nome"]

            # Salvando Relacionamentos e Opiniões
            for amigo in npc.get("relacionamentos", {}).get("amigos", []):
                if (npc_ids.get(amigo) is None):
                    continue
                self.insert_relacionamento(npc_ids[npc_name], npc_ids[amigo], "amigo")

            for inimigo in npc.get("relacionamentos", {}).get("inimigos", []):
                if (npc_ids.get(inimigo) is None):
                    continue
                self.insert_relacionamento(npc_ids[npc_name], npc_ids[inimigo], "inimigo")

            for nome, opiniao in npc.get("opinioes", {}).items():
                if (npc_ids.get(nome) is None):
                    continue
                self.insert_opiniao(npc_ids[npc_name], npc_ids[nome], opiniao)


        # Salvando Pistas, Eventos e Localizações
        for pista in data_json["pistas"]:
            self.insert_pista(pista["descricao"], pista["origem"], pista["relevancia"], caso_id)

        for evento in data_json["eventos"]:
            self.insert_evento(evento["descricao"], evento["momento"], caso_id)

        for local in data_json["localizacoes"]:
            self.insert_localizacao(local["nome"], local["descricao"], local["importancia"], caso_id)

        # Salvando Solução
        self.insert_solucao(data_json["solucao"]["resumo"], data_json["solucao"]["culpado"], caso_id)
        return caso_id

    def create_tables(self):
        logging.info("Criando tabelas...")

        # Tabela de jsons_casos
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS jsons_casos (
            id INTEGER PRIMARY KEY,
            json TEXT NOT NULL,
            caso_id INTEGER,
            FOREIGN KEY (caso_id) REFERENCES casos(id));
            ''')

        # Tabela de Casos
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS casos (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            descricao TEXT NOT NULL,
            play_count INTEGER DEFAULT 0,
            solved_count INTEGER DEFAULT 0
        );
        ''')

        # Tabela de NPCs
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS npcs (
            id INTEGER PRIMARY KEY,
            caso_id INTEGER,
            nome TEXT NOT NULL,
            historia TEXT,
            ocupacao TEXT,
            personalidade TEXT,
            motivacoes TEXT,
            honestidade TEXT,
            habilidadesEspeciais TEXT,
            localizacaoDuranteCrime TEXT,
            culpado BOOLEAN,
            json TEXT,
            FOREIGN KEY (caso_id) REFERENCES casos(id)
        );
        ''')

        # Tabela de Sessões
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessoes (
            session_id TEXT PRIMARY KEY,
            data_inicio DATETIME DEFAULT CURRENT_TIMESTAMP,
            caso_id INTEGER,
            FOREIGN KEY (caso_id) REFERENCES casos(id)
        );
        ''')

        # Tabela de Histórico de Conversa
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_conversa (
            id INTEGER PRIMARY KEY,
            session_id TEXT,
            npc_id INTEGER,
            mensagem TEXT NOT NULL,
            message_type TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessoes(session_id),
            FOREIGN KEY (npc_id) REFERENCES npcs(id)
        );
        ''')

        # Tabela de Resultados
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS resultados (
            session_id TEXT PRIMARY KEY,
            npc_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessoes(session_id)
        );
        ''')

        # Tabela de Relacionamentos
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS npc_relacionamentos (
            id INTEGER PRIMARY KEY,
            npc_id INTEGER,
            relacionado_id INTEGER,
            tipo_relacionamento TEXT NOT NULL,
            FOREIGN KEY (npc_id) REFERENCES npcs(id),
            FOREIGN KEY (relacionado_id) REFERENCES npcs(id)
        );
        ''')

        # Tabela de Opiniões
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS npc_opinioes (
            id INTEGER PRIMARY KEY,
            npc_id INTEGER,
            sobre_npc_id INTEGER,
            opiniao TEXT NOT NULL,
            FOREIGN KEY (npc_id) REFERENCES npcs(id),
            FOREIGN KEY (sobre_npc_id) REFERENCES npcs(id)
        );
        ''')

        # Tabela de Pistas
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS pistas (
            id INTEGER PRIMARY KEY,
            descricao TEXT NOT NULL,
            origem TEXT NOT NULL,
            relevancia TEXT NOT NULL,
            caso_id INTEGER,
            FOREIGN KEY (caso_id) REFERENCES casos(id)
        );
        ''')

        # Tabela de Eventos
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY,
            descricao TEXT NOT NULL,
            momento TEXT NOT NULL,
            caso_id INTEGER,
            FOREIGN KEY (caso_id) REFERENCES casos(id)
        );
        ''')

        # Tabela de Localizações
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS localizacoes (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            descricao TEXT NOT NULL,
            importancia TEXT NOT NULL,
            caso_id INTEGER,
            FOREIGN KEY (caso_id) REFERENCES casos(id)
        );
        ''')

        # Tabela de Soluções
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS solucoes (
            id INTEGER PRIMARY KEY,
            resumo TEXT NOT NULL,
            culpado TEXT NOT NULL,
            caso_id INTEGER,
            FOREIGN KEY (caso_id) REFERENCES casos(id)
        );
        ''')

        logging.info("Tabelas criadas com sucesso!")
        self.conn.commit()

    def get_json_caso(self, caso_id):
        self.cursor.execute('''
        SELECT json FROM jsons_casos WHERE caso_id = ?;
        ''', (caso_id,))
        return self.cursor.fetchone()

    def get_cases(self):
        self.cursor.execute('''
        SELECT * FROM casos;
        ''')
        return self.cursor.fetchall()

    def get_case(self, caso_id):
        self.cursor.execute('''
        SELECT * FROM casos WHERE id = ?;
        ''', (caso_id,))
        return self.cursor.fetchone()

    def get_npcs(self, caso_id):
        self.cursor.execute('''
        SELECT * FROM npcs WHERE caso_id = ?;
        ''', (caso_id,))
        return self.cursor.fetchall()

    def get_npc(self, npc_id):
        self.cursor.execute('''
        SELECT * FROM npcs WHERE id = ?;
        ''', (npc_id,))
        return self.cursor.fetchone()

    def get_json_npc(self, npc_id):
        self.cursor.execute('''
        SELECT json FROM npcs WHERE id = ?;
        ''', (npc_id,))
        return self.cursor.fetchone()

    def get_sessao(self, session_id):
        self.cursor.execute('''
        SELECT * FROM sessoes WHERE session_id = ?;
        ''', (session_id,))
        return self.cursor.fetchone()

    def get_message_history(self, session_id, npc_id):
        self.cursor.execute('''
        SELECT * FROM historico_conversa WHERE session_id = ? AND npc_id = ? ORDER BY timestamp ASC;
        ''', (session_id, npc_id))
        return self.cursor.fetchall()

    def get_resultado(self, session_id):

        self.cursor.execute('''
        SELECT * FROM resultados WHERE session_id = ?;
        ''', (session_id,))
        return self.cursor.fetchone()

    def insert_json_caso(self, json_in, caso_id):
        if type(json_in) is dict:
            json_in = json.dumps(json_in)
        self.cursor.execute('''
        INSERT INTO jsons_casos (json, caso_id) VALUES (?, ?);
        ''', (json_in, caso_id))
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_caso(self, nome, descricao):
        self.cursor.execute('''
        INSERT INTO casos (nome, descricao) VALUES (?, ?);
        ''', (nome, descricao))
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_npc(self, caso_id, nome, historia, ocupacao, personalidade, motivacoes, honestidade,
                   habilidadesEspeciais, localizacaoDuranteCrime, culpado, json_in):

        if type(json_in) is dict:
            json_in = json.dumps(json_in)
        self.cursor.execute('''
        INSERT INTO npcs (caso_id, nome, historia, ocupacao, personalidade, motivacoes, honestidade, habilidadesEspeciais, localizacaoDuranteCrime, culpado, json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', (caso_id, nome, historia, ocupacao, personalidade, motivacoes, honestidade, habilidadesEspeciais,
              localizacaoDuranteCrime, culpado, json_in))
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_sessao(self, session_id, caso_id):
        self.cursor.execute('''
        INSERT INTO sessoes (session_id, caso_id) VALUES (?, ?);
        ''', (session_id, caso_id))
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_message_history(self, session_id, npc_id, mensagem, message_type):
        self.cursor.execute('''
        INSERT INTO historico_conversa (session_id, npc_id, mensagem, message_type) VALUES (?, ?, ?, ?);
        ''', (session_id, npc_id, mensagem, message_type))
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_resultado(self, session_id, resultado):
        self.cursor.execute('''
        INSERT INTO resultados (session_id, resultado) VALUES (?, ?);
        ''', (session_id, resultado))
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_relacionamento(self, npc_id, relacionado_id, tipo_relacionamento):
        print("Inserindo relacionamento" + str(npc_id) + " " + str(relacionado_id) + " " + str(tipo_relacionamento))
        self.cursor.execute('''
        INSERT INTO npc_relacionamentos (npc_id, relacionado_id, tipo_relacionamento) VALUES (?, ?, ?);
        ''', (npc_id, relacionado_id, tipo_relacionamento))
        print("Relacionamento inserido")
        self.conn.commit()
        print("Relacionamento commitado")
        print(self.cursor.lastrowid)
        return self.cursor.lastrowid

    def insert_opiniao(self, npc_id, sobre_npc_id, opiniao):
        self.cursor.execute('''
        INSERT INTO npc_opinioes (npc_id, sobre_npc_id, opiniao) VALUES (?, ?, ?);
        ''', (npc_id, sobre_npc_id, opiniao))
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_pista(self, descricao, origem, relevancia, caso_id):
        self.cursor.execute('''
        INSERT INTO pistas (descricao, origem, relevancia, caso_id) VALUES (?, ?, ?, ?);
        ''', (descricao, origem, relevancia, caso_id))
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_evento(self, descricao, momento, caso_id):
        self.cursor.execute('''
        INSERT INTO eventos (descricao, momento, caso_id) VALUES (?, ?, ?);
        ''', (descricao, momento, caso_id))
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_localizacao(self, nome, descricao, importancia, caso_id):
        self.cursor.execute('''
        INSERT INTO localizacoes (nome, descricao, importancia, caso_id) VALUES (?, ?, ?, ?);
        ''', (nome, descricao, importancia, caso_id))
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_solucao(self, resumo, culpado, caso_id):
        self.cursor.execute('''
        INSERT INTO solucoes (resumo, culpado, caso_id) VALUES (?, ?, ?);
        ''', (resumo, culpado, caso_id))
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_answer(self, session_id, npc_id):
        self.cursor.execute('''
        INSERT INTO resultados (session_id, npc_id) VALUES (?, ?);
        ''', (session_id, npc_id))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_play_count(self, caso_id):
        self.cursor.execute('''
        UPDATE casos SET play_count = play_count + 1 WHERE id = ?;
        ''', (caso_id,))
        self.conn.commit()

    def get_news_cases(self):
        self.cursor.execute('''
        SELECT * FROM casos ORDER BY play_count ASC LIMIT 2;
        ''')
        cases = self.cursor.fetchall()
        return cases
