<template>
  <form class="space-y-5" @submit.prevent="submeter">

    <!-- Título -->
    <div>
      <label class="block text-sm font-medium text-slate-700 mb-1">Título <span class="text-red-500">*</span></label>
      <input
        v-model="form.titulo"
        type="text"
        placeholder="Ex: Bancária Maio 2026"
        class="w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        :class="erros.titulo ? 'border-red-400' : 'border-slate-200'"
      />
      <p v-if="erros.titulo" class="mt-1 text-xs text-red-500">{{ erros.titulo }}</p>
    </div>

    <!-- Empresa — apenas admin_ia16 -->
    <div v-if="isAdmin">
      <label class="block text-sm font-medium text-slate-700 mb-1">Empresa <span class="text-red-500">*</span></label>
      <select
        v-model="form.empresa_id"
        class="w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        :class="erros.empresa_id ? 'border-red-400' : 'border-slate-200'"
      >
        <option value="">Selecione a empresa</option>
        <option v-for="e in empresas" :key="e.id" :value="e.id">{{ e.nome }}</option>
      </select>
      <p v-if="erros.empresa_id" class="mt-1 text-xs text-red-500">{{ erros.empresa_id }}</p>
    </div>

    <!-- Tipo de conciliação -->
    <div>
      <label class="block text-sm font-medium text-slate-700 mb-1">Tipo de conciliação <span class="text-red-500">*</span></label>
      <select
        v-model="form.tipo_conciliacao"
        class="w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        :class="erros.tipo_conciliacao ? 'border-red-400' : 'border-slate-200'"
      >
        <option value="">Selecione o tipo</option>
        <option v-for="t in tipos" :key="t.valor" :value="t.valor">{{ t.label }}</option>
      </select>
      <p v-if="erros.tipo_conciliacao" class="mt-1 text-xs text-red-500">{{ erros.tipo_conciliacao }}</p>
    </div>

    <!-- Período -->
    <div class="grid grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1">Início do período <span class="text-red-500">*</span></label>
        <input
          v-model="form.periodo_inicio"
          type="date"
          class="w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          :class="erros.periodo_inicio ? 'border-red-400' : 'border-slate-200'"
        />
        <p v-if="erros.periodo_inicio" class="mt-1 text-xs text-red-500">{{ erros.periodo_inicio }}</p>
      </div>
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1">Fim do período <span class="text-red-500">*</span></label>
        <input
          v-model="form.periodo_fim"
          type="date"
          class="w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          :class="erros.periodo_fim ? 'border-red-400' : 'border-slate-200'"
        />
        <p v-if="erros.periodo_fim" class="mt-1 text-xs text-red-500">{{ erros.periodo_fim }}</p>
      </div>
    </div>

    <!-- Erro geral -->
    <div v-if="erroGeral" class="bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg px-4 py-3">
      {{ erroGeral }}
    </div>

    <!-- Ações -->
    <div class="flex items-center justify-end gap-3 pt-2">
      <button
        type="button"
        class="px-4 py-2 text-sm text-slate-600 hover:text-slate-800 transition-colors"
        :disabled="salvando"
        @click="$emit('cancelar')"
      >
        Cancelar
      </button>
      <button
        type="submit"
        class="px-5 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        :disabled="salvando"
      >
        {{ salvando ? 'Criando...' : 'Criar Conciliação' }}
      </button>
    </div>

  </form>
</template>

<script setup lang="ts">
import { novaConciliacaoSchema } from '~/schemas/conciliacao.schema'

const props = defineProps<{ isAdmin: boolean }>()
const emit = defineEmits<{ cancelar: []; criada: [id: string] }>()

const { criar } = useConciliacoes()
const { empresas, carregar: carregarEmpresas } = useEmpresas()

onMounted(() => { if (props.isAdmin) carregarEmpresas() })

const form = reactive({
  titulo: '',
  tipo_conciliacao: '',
  periodo_inicio: '',
  periodo_fim: '',
  empresa_id: '',
})

const erros = reactive<Record<string, string>>({})
const erroGeral = ref<string | null>(null)
const salvando = ref(false)

const tipos = [
  { valor: 'extrato_anotado', label: 'Extrato Anotado' },
]


function limparErros() {
  Object.keys(erros).forEach(k => delete erros[k])
  erroGeral.value = null
}

async function submeter() {
  limparErros()

  const resultado = novaConciliacaoSchema.safeParse(form)
  if (!resultado.success) {
    resultado.error.errors.forEach(e => {
      erros[e.path[0] as string] = e.message
    })
    return
  }

  if (props.isAdmin && !form.empresa_id) {
    erros.empresa_id = 'Selecione a empresa'
    return
  }

  salvando.value = true
  try {
    const payload = {
      titulo: form.titulo,
      tipo_conciliacao: form.tipo_conciliacao,
      periodo_inicio: form.periodo_inicio,
      periodo_fim: form.periodo_fim,
      ...(props.isAdmin && form.empresa_id ? { empresa_id: form.empresa_id } : {}),
    }
    const criada = await criar(payload)
    emit('criada', criada.id)
  } catch (e: any) {
    erroGeral.value = e.message ?? 'Não foi possível criar a conciliação.'
  } finally {
    salvando.value = false
  }
}
</script>
