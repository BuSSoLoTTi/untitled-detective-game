<template>
  <div class="npc" :style="{ backgroundColor: color }">
    <img v-if="npc.icon" :src="npc.icon" alt="Icone do NPC" class="npc-icon" />
    <p v-if="npc.npc_name">{{ npc.npc_name }}</p>
  </div>
</template>

<script>
export default {
  name: "NpcView",
  props: {
    npc: {
      type: Object,
      required: true
    },
    color: {
      type: String,
      default: 'white'  // Uma cor padrão caso nenhuma seja fornecida
    }
  },
}
</script>

<style scoped>
.npc {
  flex: 1;
  height: 25vh;
  margin: 0 5px;
  background-color: v-bind(npc.color);
  border-radius: 5px;
}


.npc-icon {
  width: 30px; /* ou o tamanho que desejar */
  height: 30px;
}
</style>
