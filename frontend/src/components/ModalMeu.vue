<template>
  <div v-if="isVisible" class="modal-overlay">
    <div class="modal">

      <h2>{{ texto }}</h2>

      <button @click="closeModal">OK</button>


    </div>
  </div>
</template>

<script>
export default {
  name: 'ModalMeu',
  props: {
    isVisible: {
      type: Boolean,
      default: false
    },
    texto: {
      type: String,
      default: ''
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
