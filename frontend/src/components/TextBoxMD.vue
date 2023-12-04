<template>
  <div class="text-box" v-if="npc">
    <p v-for="msg in npc.npc_message_array"
       :key="msg.content"
    >
      <strong v-if="msg.role === 'user'">Você:</strong>
      <strong v-else-if="msg.role === 'assistant'" :style="{ color: color_npc }">{{ npc.npc_name }}:</strong>
      {{ msg.content }}
    </p>
    <p v-if="current_message !== ''">
      <strong :style="{ color: color_npc }">{{ npc.npc_name }}:</strong> {{ current_message }}
    </p>
  </div>
</template>

<script>


export default {
  name: "TextBoxMD",
  props: {
    npc: {
      type: Object,
      required: true
    },
    current_message: {
      type: String,
      default: ''
    },
    color_npc: {
      type: String,
      default: 'red'  // Uma cor padrão caso nenhuma seja fornecida
    }
  },

}


</script>

<style>
.text-box {


  border-radius: 5px;
  width: calc(100% - 4vw); /* Largura ajustada para considerar os paddings */
  height: 60vh; /* 60% da altura da tela */
  margin-top: 2vh; /* 2% da altura da tela */
  border: 2px solid #000;
  background-color: #2c2c2c; /* Fundo mais escuro */
  color: #e0e0e0; /* Cor de texto clara */
  overflow-y: auto;
  white-space: pre-line;
}
</style>