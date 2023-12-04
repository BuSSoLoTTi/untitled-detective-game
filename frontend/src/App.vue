<template>
<TermsModal :is-visible="showTermsModal" @close="showTermsModal = false"/>
  <ModalMeu :is-visible="showResultModal" :texto="resultText" @close="showResultModal = false"/>

  <div v-if="!showTermsModal && !showResultModal" class="main-container">
    <!-- Container dos NPCs -->
    <div class="characters-container">
      <div class="npc-container">
        <NpcView v-for="(npc, index) in npcs" :key="npc.id" :npc="npc" :color="colors[index % colors.length]"
                 @click="setActiveNpc(npc)"
                 :class="{ active: activeNpc === npc.npc_index, desaturated: activeNpc !== npc.npc_index && activeNpc !== null }"/>
      </div>
      <div class="officer-container">
        <NpcView :npc="officer"
                 :key="officer.name"
                 @click="setActiveNpc(officer)"
                 :class="{ active: activeNpc === officer.index_id }"
        />
      </div>
    </div>
    <!-- Caixa de Texto -->
    <TextBox :npc="npcs[activeNpc -1 ]" ref="textBox" :color="colors[activeNpc % colors.length]"
             :current_message="current_message"/>

    <TextBoxMD v-if="activeNpc == officer.index_id" :npc="officer" ref="textBox" :color="white" :current_message="current_message"/>

    <OpcaoDropdown :opcoes="opcoesList"/>
    <input v-if="activeNpc != officer.index_id" class="user-input" v-model="userInput" type="text" placeholder="Digite sua mensagem..."
           @keyup.enter="sendMessage"/>
  </div>
</template>


<script>
import NpcView from "@/components/Npc.vue";
import OpcaoDropdown from "@/components/Opcao.vue";
import TextBox from "@/components/TextBox.vue";
import TextBoxMD from "@/components/TextBoxMD.vue";
import TermsModal from "@/components/TermsModal.vue";
import ModalMeu from "@/components/ModalMeu.vue";
import io from 'socket.io-client';

export default {
  components: {
    NpcView,
    OpcaoDropdown,
    TextBox,
    TextBoxMD,
    TermsModal,
    ModalMeu
  },
  data() {
    return {
      npcs: [],
      case_id: null,
      officer: {},
      activeNpc: 0,
      userInput: '',
      current_message: '',
      showTermsModal: true,
      showResultModal: false,
      resultText: '',
      socket: null,
      lock_npc: false,
      opcoesList: [
        {
          nome: "Iniciar",
          funcao: () => {
            this.opcoesList[0].loading = true;
            this.setup();
          },
          loading: false
        },
        {
          nome: "Definir Culpado",
          funcao: () => {
             this.submitAnswer();
          },
          loading: false
        }
      ],
      colors: ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown']
    }
  },
  created() {
    this.initSocket();
  },
  methods: {

    initSocket() {
      this.socket = io(process.env.VUE_APP_SOCKET_URL);


      this.socket.on('message', (data) => {
        this.current_message += data;
        this.scrollToBottom();
        // Você pode processar a data aqui ou definir em algum data propertys
      });

      this.socket.on('finish_chat', (data) => {

        this.current_message = '';
        this.npcs[this.activeNpc - 1].npc_message_array.push({
          role: 'assistant',
          content: data
        });
        this.npcs = [...this.npcs];
        this.lock_npc = false;
      });


      this.socket.on('setup', (data) => {
        this.opcoesList[0].loading = false;
        this.npcs = data.npc_array;
        this.officer = {
          id: 0,
          ncp_index: 0,
          npc_name: "Oficial",
          npc_message_array: [],
          color: "gray"
        };
        this.case_id = data.case_id;
        this.activeNpc = this.officer.index_id;
      });

      this.socket.on('message_officer', (data) => {
        this.current_message += data;
        // Você pode processar a data aqui ou definir em algum data propertys
      });

      this.socket.on('finish_chat_officer', (data) => {
        this.current_message = '';
        this.officer.npc_message_array.push({
          role: 'assistant',
          content: data
        });
        this.lock_npc = false;
      });

      this.socket.on('finish_case', (data) => {
        console.log(data);
        this.resultText = data;
        this.showResultModal = true;
      });

      this.socket.on('new_case', (data) => {
        console.log(data);
      });

    },

    setActiveNpc(npc) {
      if (this.lock_npc) {
        return;
      }
      console.log(npc);
      console.log(this.npcs[npc.npc_id - 1]);
      this.activeNpc = npc.npc_index;
    },

    setup() {
      this.activeNpc = 0;
      this.lock_npc = true;
      this.socket.emit('setup', {
        case_id: this.case_id
      });
    },

    sendMessage() {
    this.lock_npc = true;
    console.log(this.userInput);

    // Verificar se o userInput segue o padrão "new_case:alguma_coisa/alguma_coisa"
    const pattern = /^new_case:(.+?)\/(.+)$/;
    const matches = this.userInput.match(pattern);

    if (matches) {
        const pass = matches[1];
        const quantidade = parseInt(matches[2]);

        // Se pass for igual a "pass", faça algo com quantidade
        if (pass === "12354") {
            // Aqui, você pode usar "quantidade" para qualquer outra lógica
            this.createCase(quantidade);  // Chame sua função
        } else {
            // Faça alguma coisa se pass não for "pass"
        }

        this.userInput = '';  // Limpar o userInput
        return;
      }

      if (this.userInput.trim()) {
        this.npcs[this.activeNpc - 1].npc_message_array.push({
          role: 'user',
          content: this.userInput
        });
        this.npcs = [...this.npcs];
        this.socket.emit('send_message', {
          npc_id: this.npcs[this.activeNpc - 1].npc_id,
          text: this.userInput,
          case_id: this.case_id
        });
        this.userInput = '';
      }
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const box = this.$refs.textBox;
        box.scrollTop = box.scrollHeight;
      });
    },

    submitAnswer() {
      this.lock_npc = true;
      this.opcoesList[1].loading = true;
      this.socket.emit('submit_answer', {
        case_id: this.case_id,
        npc_id: this.npcs[this.activeNpc - 1].npc_id
      });
    },
    createCase(quantity) {
      this.socket.emit('new_case', {
        quantity: quantity
      });
    }
  }
}

</script>

<style>
#app {
  margin: 0;
  padding: 0;
}


html, body {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden; /* Previne scroll desnecessário */
  background-color: #1c1c1c;
}


.active {
  border: 3px solid gold;
}

.main-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding-left: 2vw; /* Adiciona um pequeno padding à esquerda para dar espaço */
  padding-right: 2vw; /* Adiciona um pequeno padding à direita para dar espaço */
  align-items: stretch; /* isso irá esticar os elementos filhos para preencher toda a largura do container */
}

.npc-container {
  display: flex;
  margin-top: 2vh; /* 2% da altura da tela */
  flex-grow: 1;
  width: 75%; /* Toma a largura total disponível */
  justify-content: flex-start; /* Alinha os NPCs à esquerda dentro de seu container */
}

.desaturated {
  filter: grayscale(80%); /* 50% desaturação, ajuste conforme desejado */
}


.officer-container {
  display: flex;
  margin-top: 2vh; /* 2% da altura da tela */
  width: 25vw; /* Toma a largura total disponível */
}

.characters-container {
  display: flex;
  flex-direction: row;
  width: calc(100% - 4vw);
  height: auto; /* isso fará com que o container se ajuste à altura de seus elementos filhos */
}


.user-input {
  width: calc(100% - 4vw);
  height: 40px;
  margin-top: 2vh;
  border: 1px solid #444; /* Borda mais escura */
  background-color: #333; /* Fundo escuro */
  color: #e0e0e0; /* Cor de texto clara */
  border-radius: 5px;
  font-size: 16px;
  outline: none;
  transition: border-color 0.3s; /* Transição suave ao focar */
}

.user-input:focus {
  border-color: #555; /* Mudança de cor ao focar para um tom ligeiramente mais claro */
  background-color: #3a3a3a; /* Um pouco mais claro ao focar */
}
</style>
