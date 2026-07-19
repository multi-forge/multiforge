<h2 align="center">
  🔧 Forge Imager
  <br><br>
</h2>

### Sobre

O Forge Imager é uma ferramenta para baixar e gravar imagens de sistemas operacionais em computadores de placa única (SBCs). Ele verifica o disco de destino antes de gravar, valida o checksum e verifica a imagem após a gravação, garantindo que um download corrompido ou a seleção do disco errado não danifiquem seu dispositivo.

> **Nota:** Este projeto é um fork do [Armbian Imager](https://github.com/armbian/imager), adaptado para o ecossistema Forge.

### Recursos

- Compatível com múltiplas placas, incluindo filtragem e metadados específicos de cada placa
- Verificações de segurança do disco, validação de checksum e verificação pós-gravação
- Compilações nativas para Linux, Windows e macOS (suportando x64 e ARM64)
- Interface multilíngue que segue o idioma padrão do seu sistema operacional
- Atualizações integradas no próprio aplicativo
- Executável leve com poucas dependências de execução

## Download

Binários pré-compilados estão disponíveis para todas as plataformas suportadas.

| <a href="https://github.com/multi-forge/multi-forge/releases"><img src="https://cdn.jsdelivr.net/npm/simple-icons@v11/icons/apple.svg" width="24"><br><strong>macOS</strong></a> | <a href="https://github.com/multi-forge/multi-forge/releases"><img src="https://cdn.jsdelivr.net/npm/simple-icons@v11/icons/windows11.svg" width="24"><br><strong>Windows</strong></a> | <a href="https://github.com/multi-forge/multi-forge/releases"><img src="https://cdn.jsdelivr.net/npm/simple-icons@v11/icons/linux.svg" width="24"><br><strong>Linux</strong></a> |
|:---:|:---:|:---:|
| Intel e Apple Silicon | x64 e ARM64 | x64 e ARM64 |
| <code>.dmg</code> / <code>.app.zip</code> | <code>.exe</code> / <code>.msi</code> | <code>.deb</code> / <code>.AppImage</code> |

## Como Funciona

1. **Escolha um fabricante.** Selecione um dos fabricantes de SBC suportados ou carregue seu próprio arquivo de imagem local.
2. **Escolha uma placa.** As placas mostram fotos e metadados descritivos.
3. **Escolha uma imagem.** Selecione desktop ou servidor, ramificação do kernel e se deseja uma compilação estável, nightly ou rolling release.
4. **Grave.** O aplicativo baixa, descompacta, grava e verifica tudo de forma automatizada.

## Customização

- Tema: claro, escuro ou automático (seguindo a configuração do sistema)
- Modo desenvolvedor: ativa logs detalhados e abre o visualizador de logs integrado
- Idioma: 18 idiomas suportados, detectados automaticamente com base no seu sistema

## Suporte de Plataforma

| Plataforma | Arquitetura | Notas |
|------------|-------------|-------|
| macOS | Intel x64 | Suporte completo |
| macOS | Apple Silicon | Compilação ARM64 nativa, suporte a Touch ID |
| Windows | x64 | Requer privilégios de Administrador |
| Windows | ARM64 | Compilação ARM64 nativa, requer privilégios de Administrador |
| Linux | x64 | Usa lsblk para detecção de discos e UDisks2/polkit para acesso elevado ao dispositivo |
| Linux | ARM64 | Compilação ARM64 nativa |

### Idiomas Suportados

Alemão, Chinês, Coreano, Croata, Espanhol, Francês, Holandês, Inglês, Italiano, Japonês, Polonês, Português, Português (Brasil), Russo, Sueco, Esloveno, Turco, Ucraniano

## Desenvolvimento

As instruções de configuração, compilação e layout do projeto estão detalhadas em [DEVELOPMENT.md](DEVELOPMENT.md).

## Créditos

- Baseado no [Armbian Imager](https://github.com/armbian/imager) — projeto original
- [Tauri](https://tauri.app/) — Framework de desenvolvimento
- [i18next](https://www.i18next.com/) — Internacionalização e traduções
- [Lucide](https://lucide.dev/) — Pacote de ícones

---

<p align="center">
  <sub>Feito com ❤️ pela comunidade Forge</sub>
</p>
