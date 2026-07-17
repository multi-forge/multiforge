# 🏗️ Arquitetura do MultiForge

Esta seção descreve a arquitetura geral do ecossistema MultiForge e como seus componentes principais interagem.

---

## 🗺️ Visão Geral dos Componentes

O MultiForge é composto por cinco pilares fundamentais que cooperam para simplificar o provisionamento de hardware ARM:

```text
┌─────────────────────────────────────────────────────────┐
│                     ForgeImager                         │
│   (Interface visual para gravação e injeção de config)  │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼ (injeta forge.yaml)
┌─────────────────────────────────────────────────────────┐
│                       ForgeOS                           │
│   (Imagem base de SO rodando Provisioner e Agent)       │
└──────────────┬───────────────────────────┬──────────────┘
               │                           │
               ▼ (consulta metadados)      ▼ (instala softwares)
┌────────────────────────────┐    ┌───────────────────────┐
│          ForgeDB           │    │       ForgeHub        │
│   (Banco de compatibilidade│    │ (Catálogo e runtime   │
│       e especificações)    │    │      de módulos)      │
└────────────────────────────┘    └───────────┬───────────┘
                                              │
                                              ▼ (instala no SO)
                                  ┌───────────────────────┐
                                  │     ForgeModules      │
                                  │  (Softwares e perfis) │
                                  └───────────────────────┘
```

---

## 1. 🗄️ ForgeDB
O centralizador de conhecimento técnico e compatibilidade. 
* Mapeia os dispositivos (SoC, WiFi, barramentos de hardware) e previne incompatibilidades no processo de gravação.
* Define quais DTBs, kernels e firmwares devem ser utilizados para cada box ou SBC.

## 2. 🔌 ForgeHub
O repositório de módulos e marketplace operacional.
* Organiza pacotes de software com manifestos descritivos.
* Provê os metadados necessários para download e execução de soluções pré-empacotadas de automação, mídia ou inteligência artificial.

## 3. 💿 ForgeOS
O sistema operacional mínimo e base.
* O ForgeOS é enxuto, carregando apenas drivers, kernel compatível, DTB correto e os runtimes auxiliares (CLI, Agent e Provisioner).
* Ele cresce sob demanda através da instalação de perfis e módulos providos pelo ForgeHub.

## 4. 💾 ForgeImager
A ferramenta de gravação e parametrização.
* Permite escolher o dispositivo, baixar a imagem correta utilizando as definições do ForgeDB e configurar credenciais/rede sem remontar a imagem base, injetando um arquivo declarativo `forge.yaml` no boot.

## 5. 📦 ForgeModules
O catálogo de aplicações modulares.
* Softwares declarativos com dependências estruturadas e scripts de ciclo de vida gerenciados no dispositivo por meio da Forge CLI.
