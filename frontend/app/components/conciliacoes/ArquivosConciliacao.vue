<template>
  <div id="secao-upload-arquivos" class="bg-white rounded-xl border border-slate-200">

    <!-- Cabeçalho -->
    <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100">
      <h3 class="text-sm font-semibold text-slate-700">Arquivos vinculados</h3>
      <span class="text-xs text-slate-400">{{ arquivos.length }} arquivo(s)</span>
    </div>

    <!-- Formulário de upload -->
    <div v-if="podeEnviar" class="px-6 py-4 border-b border-slate-100 bg-slate-50">
      <div class="flex flex-wrap items-end gap-3">

        <div class="flex-1 min-w-48">
          <label class="block text-xs font-medium text-slate-600 mb-1">Tipo de arquivo</label>
          <select
            v-model="tipoSelecionado"
            class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          >
            <option value="">Selecione o tipo</option>
            <option v-for="(label, valor) in tiposArquivo" :key="valor" :value="valor">{{ label }}</option>
          </select>
        </div>

        <div class="flex-1 min-w-48">
          <label class="block text-xs font-medium text-slate-600 mb-1">Arquivo (.xlsx, .xls)</label>
          <input
            ref="inputRef"
            type="file"
            accept=".xlsx,.xls"
            class="w-full text-sm text-slate-600 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            @change="onArquivoSelecionado"
          />
        </div>

        <button
          class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors shrink-0"
          :disabled="enviando || !arquivoSelecionado || !tipoSelecionado"
          @click="onEnviar"
        >
          {{ enviando ? 'Enviando...' : 'Enviar arquivo' }}
        </button>

      </div>

      <p v-if="erroUpload" class="mt-2 text-xs text-red-500">{{ erroUpload }}</p>
      <p v-if="sucesso" class="mt-2 text-xs text-green-600">Arquivo enviado com sucesso.</p>
    </div>

    <!-- Carregando -->
    <div v-if="carregando" class="px-6 py-8 text-center text-sm text-slate-400">
      Carregando arquivos...
    </div>

    <!-- Vazio -->
    <div v-else-if="arquivos.length === 0" class="px-6 py-12 text-center">
      <svg class="w-10 h-10 text-slate-300 mx-auto mb-3" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
      </svg>
      <p class="text-sm text-slate-500">Nenhum arquivo enviado para esta conciliação.</p>
      <p class="text-xs text-slate-400 mt-1">Envie arquivos para iniciar o processamento.</p>
    </div>

    <!-- Lista de arquivos -->
    <ul v-else class="divide-y divide-slate-50">
      <li v-for="a in arquivos" :key="a.id" class="px-6 py-4">

        <!-- Linha principal -->
        <div class="flex items-center justify-between gap-4">
          <div class="min-w-0">
            <p class="text-sm text-slate-700 font-medium truncate">{{ a.nome_original }}</p>
            <p class="text-xs text-slate-400 mt-0.5">
              {{ tiposArquivo[a.tipo_arquivo] ?? a.tipo_arquivo }} ·
              {{ formatarTamanho(a.tamanho_bytes) }} ·
              {{ dataFormatada(a.criado_em) }}
            </p>
          </div>

          <div class="flex items-center gap-3 shrink-0">
            <span
              class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
              :class="statusClasse(a.status)"
            >
              {{ statusArquivoLabels[a.status] ?? a.status }}
            </span>

            <!-- Botão reenviar: quando arquivo não está mais disponível -->
            <span
              v-if="a.arquivo_disponivel === false || a.excluido_em"
              class="text-xs text-amber-600 font-medium"
            >
              Reenviar necessário
            </span>

            <button
              v-if="a.status !== 'lido' && (a.arquivo_disponivel !== false)"
              class="text-xs text-red-500 hover:text-red-700 transition-colors"
              @click="onRemover(a.id)"
            >
              Remover
            </button>
          </div>
        </div>

        <!-- Linha de retenção -->
        <div v-if="a.modo_retencao" class="mt-2 flex flex-wrap items-center gap-3 text-xs">

          <!-- Persistente -->
          <span
            v-if="a.modo_retencao === 'persistente'"
            class="inline-flex items-center gap-1 text-teal-600"
          >
            <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" />
            </svg>
            Armazenado de forma persistente
          </span>

          <!-- Temporário disponível -->
          <span
            v-else-if="a.modo_retencao === 'temporario' && a.arquivo_disponivel && a.expira_em"
            class="inline-flex items-center gap-1 text-blue-600"
          >
            <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Disponível até {{ dataHoraFormatada(a.expira_em) }}
          </span>

          <!-- Temporário expirado -->
          <span
            v-else-if="a.modo_retencao === 'temporario' && !a.arquivo_disponivel"
            class="inline-flex items-center gap-1 text-amber-600"
          >
            <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
            </svg>
            Arquivo expirado. Para reprocessar, envie o arquivo novamente.
          </span>

          <!-- Somente em memória -->
          <span
            v-else-if="a.modo_retencao === 'somente_memoria'"
            class="inline-flex items-center gap-1 text-slate-500"
          >
            <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
            </svg>
            Arquivo original não armazenado pela política de retenção da empresa.
          </span>

        </div>

      </li>
    </ul>

  </div>
</template>

<script setup lang="ts">
import type { ArquivoEnviado } from '~/types/arquivo'
import { tipoArquivoLabels, statusArquivoLabels } from '~/types/arquivo'
import { validarArquivoLocal } from '~/schemas/arquivo.schema'

const props = defineProps<{
  conciliacaoId: string
  status: string
}>()

const emit = defineEmits<{ atualizada: [arquivos: ArquivoEnviado[]] }>()

const { arquivos, carregando, enviando, listar, enviar, remover } = useArquivos()

const tipoSelecionado = ref('')
const arquivoSelecionado = ref<File | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)
const erroUpload = ref<string | null>(null)
const sucesso = ref(false)

const tiposArquivo = tipoArquivoLabels

const podeEnviar = computed(() =>
  !['em_processamento', 'aprovado'].includes(props.status)
)

onMounted(async () => {
  await listar(props.conciliacaoId)
  emit('atualizada', arquivos.value)
})

function onArquivoSelecionado(e: Event) {
  const input = e.target as HTMLInputElement
  arquivoSelecionado.value = input.files?.[0] ?? null
  erroUpload.value = null
  sucesso.value = false
}

async function onEnviar() {
  if (!arquivoSelecionado.value || !tipoSelecionado.value) return
  erroUpload.value = null
  sucesso.value = false

  const erroValidacao = validarArquivoLocal(arquivoSelecionado.value)
  if (erroValidacao) {
    erroUpload.value = erroValidacao
    return
  }

  try {
    await enviar(props.conciliacaoId, arquivoSelecionado.value, tipoSelecionado.value)
    sucesso.value = true
    tipoSelecionado.value = ''
    arquivoSelecionado.value = null
    if (inputRef.value) inputRef.value.value = ''
    emit('atualizada', arquivos.value)
  } catch (e: any) {
    erroUpload.value = e.message
  }
}

async function onRemover(id: string) {
  try {
    await remover(id)
    emit('atualizada', arquivos.value)
  } catch (e: any) {
    erroUpload.value = e.message
  }
}

function statusClasse(s: string) {
  const m: Record<string, string> = {
    enviado:   'bg-blue-100 text-blue-700',
    lido:      'bg-teal-100 text-teal-700',
    invalido:  'bg-red-100 text-red-600',
    processado:'bg-green-100 text-green-700',
    erro:      'bg-red-100 text-red-700',
  }
  return m[s] ?? 'bg-slate-100 text-slate-500'
}

function formatarTamanho(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function dataFormatada(iso: string) {
  return new Date(iso).toLocaleDateString('pt-BR')
}

function dataHoraFormatada(iso: string) {
  return new Date(iso).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
}
</script>
