<template>
  <div class="max-w-2xl space-y-6">
    <div class="flex items-center gap-3">
      <NuxtLink to="/admin/empresas" class="text-gray-400 hover:text-gray-600">← Voltar</NuxtLink>
      <h1 class="text-xl font-semibold text-gray-900">Editar empresa</h1>
    </div>

    <div v-if="carregando" class="text-sm text-gray-500">Carregando...</div>

    <template v-else>

      <!-- Dados da empresa -->
      <form @submit.prevent="submeter" class="bg-white rounded-lg shadow p-6 space-y-4">
        <h2 class="text-sm font-semibold text-gray-700 border-b pb-2">Dados da empresa</h2>

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
          <label class="block text-sm font-medium text-gray-700 mb-1">CNPJ</label>
          <input
            :value="empresa?.cnpj"
            type="text"
            disabled
            class="w-full border border-gray-200 rounded px-3 py-2 text-sm bg-gray-50 text-gray-400"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select
            v-model="form.status"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="ativa">Ativa</option>
            <option value="inativa">Inativa</option>
          </select>
        </div>

        <p v-if="erroEmpresa" class="text-sm text-red-600">{{ erroEmpresa }}</p>

        <div v-if="podeEditar" class="flex gap-3 pt-2">
          <button
            type="submit"
            :disabled="salvando"
            class="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {{ salvando ? "Salvando..." : "Salvar" }}
          </button>
          <NuxtLink to="/admin/empresas" class="px-4 py-2 rounded text-sm text-gray-600 hover:bg-gray-100">
            Cancelar
          </NuxtLink>
        </div>
      </form>

      <!-- Política de retenção de arquivos -->
      <div class="bg-white rounded-lg shadow p-6 space-y-4">
        <h2 class="text-sm font-semibold text-gray-700 border-b pb-2">Política de retenção de arquivos</h2>

        <div v-if="carregandoPolitica" class="text-sm text-gray-400">Carregando política...</div>
        <div v-else-if="erroPolitica" class="text-sm text-red-500">{{ erroPolitica }}</div>

        <template v-else-if="politica">

          <!-- Visualização (todos os perfis com acesso) -->
          <dl class="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
            <div>
              <dt class="text-gray-500">Modo de retenção</dt>
              <dd class="font-medium text-gray-800">{{ modoRetencaoLabels[politica.modo_retencao] }}</dd>
            </div>
            <div>
              <dt class="text-gray-500">Retenção (horas)</dt>
              <dd class="font-medium text-gray-800">{{ politica.tempo_retencao_horas ?? '—' }}</dd>
            </div>
            <div>
              <dt class="text-gray-500">Salvar arquivo original</dt>
              <dd :class="politica.salvar_arquivo_original ? 'text-green-600' : 'text-red-500'" class="font-medium">
                {{ politica.salvar_arquivo_original ? 'Sim' : 'Não' }}
              </dd>
            </div>
            <div>
              <dt class="text-gray-500">Permitir download original</dt>
              <dd :class="politica.permitir_download_original ? 'text-green-600' : 'text-red-500'" class="font-medium">
                {{ politica.permitir_download_original ? 'Sim' : 'Não' }}
              </dd>
            </div>
            <div>
              <dt class="text-gray-500">Permitir reprocessamento sem reenvio</dt>
              <dd :class="politica.permitir_reprocessamento_sem_reenvio ? 'text-green-600' : 'text-red-500'" class="font-medium">
                {{ politica.permitir_reprocessamento_sem_reenvio ? 'Sim' : 'Não' }}
              </dd>
            </div>
            <div>
              <dt class="text-gray-500">Salvar resultado processado</dt>
              <dd :class="politica.salvar_resultado_processado ? 'text-green-600' : 'text-red-500'" class="font-medium">
                {{ politica.salvar_resultado_processado ? 'Sim' : 'Não' }}
              </dd>
            </div>
            <div>
              <dt class="text-gray-500">Salvar linhas processadas</dt>
              <dd :class="politica.salvar_linhas_processadas ? 'text-green-600' : 'text-red-500'" class="font-medium">
                {{ politica.salvar_linhas_processadas ? 'Sim' : 'Não' }}
              </dd>
            </div>
            <div>
              <dt class="text-gray-500">Excluir original após processamento</dt>
              <dd :class="politica.excluir_arquivo_original_apos_processamento ? 'text-amber-600' : 'text-green-600'" class="font-medium">
                {{ politica.excluir_arquivo_original_apos_processamento ? 'Sim' : 'Não' }}
              </dd>
            </div>
          </dl>

          <!-- Edição — apenas admin_ia16 -->
          <template v-if="podeEditar">
            <div class="border-t pt-4 mt-2">
              <p class="text-xs text-slate-400 mb-3">Editar política de retenção</p>

              <div class="grid grid-cols-2 gap-4">

                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">Modo de retenção</label>
                  <select v-model="formPolitica.modo_retencao" class="w-full border border-gray-300 rounded px-3 py-2 text-sm">
                    <option value="temporario">Temporário</option>
                    <option value="persistente">Persistente</option>
                    <option value="somente_memoria">Somente em memória</option>
                  </select>
                </div>

                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">Retenção (horas)</label>
                  <input
                    v-model.number="formPolitica.tempo_retencao_horas"
                    type="number"
                    min="1"
                    :required="formPolitica.modo_retencao === 'temporario'"
                    class="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                  />
                </div>

                <div class="flex items-center gap-2">
                  <input id="salvar_original" v-model="formPolitica.salvar_arquivo_original" type="checkbox" class="rounded" />
                  <label for="salvar_original" class="text-sm text-gray-700">Salvar arquivo original</label>
                </div>

                <div class="flex items-center gap-2">
                  <input id="permitir_dl" v-model="formPolitica.permitir_download_original" type="checkbox" class="rounded" />
                  <label for="permitir_dl" class="text-sm text-gray-700">Permitir download original</label>
                </div>

                <div class="flex items-center gap-2">
                  <input id="permitir_rep" v-model="formPolitica.permitir_reprocessamento_sem_reenvio" type="checkbox" class="rounded" />
                  <label for="permitir_rep" class="text-sm text-gray-700">Permitir reprocessamento sem reenvio</label>
                </div>

                <div class="flex items-center gap-2">
                  <input id="excluir_apos" v-model="formPolitica.excluir_arquivo_original_apos_processamento" type="checkbox" class="rounded" />
                  <label for="excluir_apos" class="text-sm text-gray-700">Excluir original após processamento</label>
                </div>

              </div>

              <p v-if="erroPoliticaSalvar" class="mt-2 text-xs text-red-500">{{ erroPoliticaSalvar }}</p>
              <p v-if="sucesso" class="mt-2 text-xs text-green-600">Política salva com sucesso.</p>

              <button
                type="button"
                :disabled="salvandoPolitica"
                class="mt-4 bg-slate-700 text-white px-4 py-2 rounded text-sm font-medium hover:bg-slate-800 disabled:opacity-50"
                @click="salvarPolitica"
              >
                {{ salvandoPolitica ? 'Salvando...' : 'Salvar política' }}
              </button>
            </div>
          </template>

        </template>
      </div>

    </template>
  </div>
</template>

<script setup lang="ts">
import { modoRetencaoLabels } from '~/types/politicaRetencaoArquivo'
import type { AtualizacaoPoliticaRetencaoArquivo } from '~/types/politicaRetencaoArquivo'

definePageMeta({ layout: "default", middleware: "auth" })

const route = useRoute()
const api = useApi()
const auth = useAuthStore()

const empresa = ref<any>(null)
const carregando = ref(true)
const salvando = ref(false)
const erroEmpresa = ref<string | null>(null)
const form = reactive({ nome: "", status: "ativa" })

const podeEditar = computed(() => auth.usuario?.perfil === 'admin_ia16')

const { politica, carregando: carregandoPolitica, salvando: salvandoPolitica, erro: erroPolitica, buscarPoliticaRetencaoArquivos, atualizarPoliticaRetencaoArquivos } = usePoliticaRetencaoArquivos()

const erroPoliticaSalvar = ref<string | null>(null)
const sucesso = ref(false)
const formPolitica = reactive<AtualizacaoPoliticaRetencaoArquivo>({
  modo_retencao: 'temporario',
  salvar_arquivo_original: true,
  salvar_resultado_processado: true,
  salvar_linhas_processadas: false,
  salvar_metadados: true,
  tempo_retencao_horas: 168,
  excluir_arquivo_original_apos_processamento: false,
  permitir_download_original: true,
  permitir_reprocessamento_sem_reenvio: true,
  ativo: true,
})

onMounted(async () => {
  try {
    empresa.value = await api.get(`/api/v1/empresas/${route.params.id}`)
    form.nome = empresa.value.nome
    form.status = empresa.value.status
  } catch (e: any) {
    erroEmpresa.value = e.message
  } finally {
    carregando.value = false
  }

  // Carregar política (qualquer perfil com acesso a esta página)
  try {
    const p = await buscarPoliticaRetencaoArquivos(route.params.id as string)
    Object.assign(formPolitica, {
      modo_retencao: p.modo_retencao,
      salvar_arquivo_original: p.salvar_arquivo_original,
      salvar_resultado_processado: p.salvar_resultado_processado,
      salvar_linhas_processadas: p.salvar_linhas_processadas,
      salvar_metadados: p.salvar_metadados,
      tempo_retencao_horas: p.tempo_retencao_horas,
      excluir_arquivo_original_apos_processamento: p.excluir_arquivo_original_apos_processamento,
      permitir_download_original: p.permitir_download_original,
      permitir_reprocessamento_sem_reenvio: p.permitir_reprocessamento_sem_reenvio,
      ativo: p.ativo,
    })
  } catch {
    // erroPolitica já capturado no composable
  }
})

async function submeter() {
  salvando.value = true
  erroEmpresa.value = null
  try {
    await api.patch(`/api/v1/empresas/${route.params.id}`, form)
    navigateTo("/admin/empresas")
  } catch (e: any) {
    erroEmpresa.value = e.message
  } finally {
    salvando.value = false
  }
}

async function salvarPolitica() {
  erroPoliticaSalvar.value = null
  sucesso.value = false
  try {
    await atualizarPoliticaRetencaoArquivos(route.params.id as string, { ...formPolitica })
    sucesso.value = true
  } catch (e: any) {
    erroPoliticaSalvar.value = e?.message ?? 'Erro ao salvar política.'
  }
}
</script>
