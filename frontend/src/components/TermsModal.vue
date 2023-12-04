<template>
  <div v-if="isVisible" class="modal-overlay">
    <div class="modal">

      <h1>Termos e Condições de Uso do Jogo</h1>

      <ol>
        <li><strong>Aceitação dos Termos e Condições</strong>
          <p>Ao acessar e usar o [Nome do Jogo], você aceita e concorda com estes termos e condições. Se não concordar
            com estes termos, não acesse ou use o jogo.</p>
        </li>

        <li><strong>Objetivo do Jogo</strong>
          <p>Este jogo foi desenvolvido como parte de um trabalho de conclusão de curso (TCC) e seu uso principal é para
            coleta de dados anônimos com fins acadêmicos.</p>
        </li>

        <li><strong>Dados Coletados</strong>
          <p>Coletamos dados de forma anônima e não armazenamos informações pessoalmente identificáveis. Os dados
            coletados são exclusivamente para fins de pesquisa acadêmica e não serão vendidos, compartilhados ou
            distribuídos a terceiros.</p>
        </li>

        <li><strong>Restrições de Uso</strong>
          <p>Você não pode: (a) descompilar, fazer engenharia reversa, desmontar ou tentar derivar o código-fonte do
            nosso jogo; (b) usar o jogo para qualquer finalidade que seja ilegal ou proibida por estes termos.</p>
        </li>

        <li><strong>Limitação de Responsabilidade</strong>
          <p>O jogo é fornecido "como está" e "conforme disponível". Não garantimos que o jogo atenderá aos seus
            requisitos ou que seu uso será ininterrupto ou livre de erros.</p>
        </li>

        <li><strong>Alterações nos Termos e Condições</strong>
          <p>Reservamo-nos o direito, a nosso critério, de alterar, modificar, adicionar ou remover partes destes termos
            a qualquer momento. É sua responsabilidade verificar regularmente se há alterações.</p>
        </li>

        <li><strong>Encerramento</strong>
          <p>Podemos encerrar ou suspender o acesso ao jogo a qualquer momento, sem aviso prévio, por qualquer
            motivo.</p>
        </li>

        <li><strong>Lei Aplicável</strong>
          <p>Estes termos serão regidos e interpretados de acordo com as leis do Brasil, sem levar em conta conflitos de
            disposições legais.</p>
        </li>

        <li><strong>Contato</strong>
          <p>Se tiver alguma dúvida sobre estes termos, entre em contato conosco pelo e-mail:
            matheus.bussolotti@sga.pucminas.br.</p>
        </li>
      </ol>


      <button @click="closeModal">Aceitar e Fechar</button>


    </div>
  </div>
</template>

<script>
export default {
  props: {
    isVisible: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    closeModal() {
      this.$emit('close');
    }
  }
}
</script>

<style>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal {
  background: #333;
  padding: 20px;
  border-radius: 5px;
  width: 80%;
  max-width: 500px;
  color: #e0e0e0;
  max-height: 90vh;    /* Limita a altura da modal a 90% da altura da viewport */
  overflow-y: auto;    /* Adiciona uma barra de rolagem vertical quando necessário */
}


.modal button {
  background-color: #555;
  color: #e0e0e0;
  border: 1px solid #444;
  border-radius: 5px;
  padding: 10px 20px;
  cursor: pointer;
  margin-top: 10px;
  outline: none;
  transition: background-color 0.3s;
}

.modal button:hover {
  background-color: #666;
}
</style>
