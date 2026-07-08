<template>
  <div class="flex flex-col h-screen overflow-hidden">

    <!-- Cabeçalho fixo, largura total, acima de tudo -->
    <LayoutAppHeader />

    <!-- Abaixo: sidebar + conteúdo -->
    <div class="flex flex-1 min-h-0 bg-slate-100 p-2 pt-2 gap-2">
      <LayoutAppSidebar />
      <main class="flex-1 overflow-y-auto bg-white rounded-xl">
        <slot />
      </main>
    </div>

  </div>
</template>
