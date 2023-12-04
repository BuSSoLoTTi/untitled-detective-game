<template>
  <div>
    <!-- Botão principal -->
    <button class="options" @click="mostrarOpcoes = !mostrarOpcoes">Opções</button>

    <!-- Opções que são mostradas/ocultadas -->
    <div v-if="mostrarOpcoes">
      <button class="option"
        v-for="opcao in opcoes"
        :key="opcao.nome"
        @click="opcao.funcao"
      >
        {{ opcao.nome }}
        <span v-if="opcao.loading" class="loading-spinner"></span>
      </button>
    </div>
  </div>
</template>


<script>
export default {
  name: 'OpcaoDropdown',
  props: {
    opcoes: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      mostrarOpcoes: false
    };
  }
};
</script>

<style scoped>

.options {
  display: block;
  margin: 0.5rem;
  padding: 0.5rem;
  border: 1px solid black;
  border-radius: 0.5rem;
  background-color: #404040;
  cursor: pointer;
}

.option {
  display: inline;
  margin: 0.5rem;
  padding: 0.5rem;
  border: 1px solid #000000;
  border-radius: 0.5rem;
  background-color: #404040;
  cursor: pointer;

}

.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top: 3px solid #fff;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}


</style>
