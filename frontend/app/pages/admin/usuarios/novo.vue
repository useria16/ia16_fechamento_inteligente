<template>
  <div class="max-w-lg">
    <div class="flex items-center gap-3 mb-6">
      <NuxtLink to="/admin/usuarios" class="text-gray-400 hover:text-gray-600">← Voltar</NuxtLink>
      <h1 class="text-xl font-semibold text-gray-900">Novo usuário</h1>
    </div>

    <form @submit.prevent="submeter" class="bg-white rounded-lg shadow p-6 space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Nome</label>
        <input
          v-model="form.nome"
          type="text"
          required
          class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">E-mail</label>
        <input
          v-model="form.email"
          type="email"
          required
          class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Perfil</label>
        <select
          v-model="form.perfil"
          class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="admin_ia16">admin_ia16</option>
          <option value="cliente_admin">cliente_admin</option>
          <option value="cliente_operador">cliente_operador</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">ID Auth (Supabase)</label>
        <input
          v-model="form.usuario_auth_id"
          type="text"
          required
          placeholder="UUID do usuário em auth.users"
          class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <p v-if="erro" class="text-sm text-red-600">{{ erro }}</p>

      <div class="flex gap-3 pt-2">
        <button
          type="submit"
          :disabled="salvando"
          class="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {{ salvando ? "Salvando..." : "Salvar" }}
        </button>
        <NuxtLink to="/admin/usuarios" class="px-4 py-2 rounded text-sm text-gray-600 hover:bg-gray-100">
          Cancelar
        </NuxtLink>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" })

const api = useApi()
const salvando = ref(false)
const erro = ref<string | null>(null)
const form = reactive({
  nome: "",
  email: "",
  perfil: "cliente_operador",
  usuario_auth_id: "",
  empresa_id: null as string | null,
})

async function submeter() {
  salvando.value = true
  erro.value = null
  try {
    await api.post("/api/usuarios", form)
    navigateTo("/admin/usuarios")
  } catch (e: any) {
    erro.value = e.message
  } finally {
    salvando.value = false
  }
}
</script>
