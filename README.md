# Udiconnect Plus - Componente Customizado para Home Assistant

Integração customizada do Home Assistant para cortinas, persianas e outros dispositivos inteligentes Udiconnect Plus.

## Recursos

- **Descoberta Automática**: Detecta todas as cortinas/persianas na sua conta Udiconnect Plus (ou seja, todas as cortinas/persianas que você tem cadastradas no aplicativo móvel)
- **Controle Completo**: Abra, feche e defina posições precisas (0-100%)
- **Atualizações em Tempo Real**: Consulta o status dos dispositivos a cada 10 segundos
- **Interface Nativa**: Configure através da interface do Home Assistant (Configurações > Integrações)

## Dispositivos Suportados

- Cortinas Udiconnect Plus
- Persianas Udiconnect Plus

IMPORTANTE: No momento, todo e qualquer dispositivo da conta será automaticamente adicionado como uma entidade do tipo [cover](https://www.home-assistant.io/integrations/cover/).

## Instalação

### Método 1: HACS (Recomendado)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

1. **Certifique-se de ter o [HACS](https://hacs.xyz/) instalado**

2. **Adicione este repositório como repositório customizado:**
   - Abra o HACS
   - Clique nos 3 pontos no canto superior direito
   - Selecione "Repositórios personalizados"
   - Cole a URL: `https://github.com/rezendeneto/udiconnect-plus-ha`
   - Selecione a categoria: "Integration"
   - Clique em "Adicionar"

3. **Instale a integração:**
   - Procure por "Udiconnect Plus" no HACS
   - Clique em "Download"
   - Reinicie o Home Assistant

4. **Configure a integração:**
   - Vá em **Configurações** > **Integrações**
   - Clique em **+ Adicionar Integração**
   - Procure por "Udiconnect Plus"
   - Digite seu email e senha do Udiconnect Plus
   - Confirme e salve

### Método 2: Instalação Manual

1. **Baixe e copie os arquivos:**
   ```bash
   # Navegue até o diretório de configuração do Home Assistant
   cd /config

   # Baixe o repositório
   wget https://github.com/rezendeneto/udiconnect-plus-ha/archive/refs/heads/master.zip
   unzip master.zip

   # Copie a integração para custom_components
   cp -r udiconnect-plus-ha-master/custom_components/udiconnect_plus custom_components/

   # Limpe os arquivos temporários
   rm -rf udiconnect-plus-ha-master master.zip
   ```

   **OU usando git:**
   ```bash
   # Clone temporariamente o repositório
   git clone https://github.com/rezendeneto/udiconnect-plus-ha.git /tmp/udiconnect-plus-ha

   # Copie apenas a pasta da integração
   cp -r /tmp/udiconnect-plus-ha/custom_components/udiconnect_plus /config/custom_components/

   # Limpe o repositório temporário
   rm -rf /tmp/udiconnect-plus-ha
   ```

2. **Reinicie o Home Assistant**

3. **Adicione a integração:**
   - Vá em **Configurações** > **Integrações**
   - Clique em **+ Adicionar Integração**
   - Procure por "Udiconnect Plus"
   - Digite seu email e senha do Udiconnect Plus
   - Confirme e salve

## Configuração

A integração é configurada inteiramente pela interface do Home Assistant:

1. Navegue até **Configurações** > **Dispositivos e Serviços**
2. Clique em **+ Adicionar Integração**
3. Procure por "Udiconnect Plus"
4. Digite suas credenciais:
   - **Email**: Seu email da conta Udiconnect Plus
   - **Senha**: Sua senha da conta Udiconnect Plus

## Uso

### Controlando Cortinas

Uma vez configuradas, suas cortinas aparecerão como entidades de cobertura no Home Assistant:

**IDs de Entidade**: `cover.<nome_do_dispositivo>`

## Informações do Dispositivo

Cada entidade de dispositivo fornece as seguintes informações:

- **ID do Dispositivo**: Identificador único para o dispositivo
- **ID da Casa**: A qual localização o dispositivo pertence
- **Modelo do Dispositivo**: Informações do modelo
- **Versão do Firmware**: Versão atual do firmware
- **Posição Atual**: Posição de 0 (fechado) a 100 (aberto)

## Opções de Configuração

### Intervalo de Atualização

O intervalo de atualização padrão é de 10 segundos. Para alterar isso, você precisará modificar `const.py`:

```python
DEFAULT_SCAN_INTERVAL = 60  # Alterar para 60 segundos
```

Em seguida, reinicie o Home Assistant.

## Solução de Problemas

### Ativar log de depuração

Adicione ao seu `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.udiconnect_plus: debug
```

Em seguida, reinicie o Home Assistant e verifique os logs.

## Informações da API

Esta integração usa a API Udiconnect Plus:

- **URL Base**: `https://AA-Brands.yaleconnect-services.com/api/YaleConnect/`
- **Autenticação**: Token de acesso via login com email/senha
- **Método de Atualização**: Polling (baseado na nuvem, sem API local)

### Endpoints da API Utilizados

- `POST /Account/Login` - Autenticação
- `POST /App/SyncAccount` - Buscar todos os dispositivos
- `POST /Curtain/SetPositionCurtain` - Definir posição absoluta

## Estrutura de Arquivos

```
udiconnect-plus-ha/
├── custom_components/
│   └── udiconnect_plus/
│       ├── translations/
│       │   └── en.json        # Traduções em inglês
│       ├── __init__.py        # Ponto de entrada do componente
│       ├── api.py             # Implementação do cliente da API
│       ├── config_flow.py     # Fluxo de configuração da interface
│       ├── const.py           # Constantes e configuração
│       ├── cover.py           # Plataforma de entidade de cobertura
│       ├── icon.png           # Ícone do componente
│       ├── icon@2x.png        # Ícone do componente (2x)
│       └── manifest.json      # Metadados do componente
├── .gitignore                 # Arquivos ignorados pelo git
├── hacs.json                  # Configuração HACS
├── info.md                    # Informações para HACS
├── LICENSE                    # Licença MIT
└── README.md                  # Este arquivo
```

## Desenvolvimento

### Testando Localmente

1. Copie o componente para o diretório `custom_components` do seu Home Assistant
2. Reinicie o Home Assistant
3. Adicione a integração através da interface
4. Verifique os logs para quaisquer erros

### Contribuindo

Esta é uma integração de engenharia reversa baseada no aplicativo móvel Udiconnect Plus. Contribuições são bem-vindas:

- Correções de bugs
- Tipos adicionais de dispositivos (fechaduras, câmeras, etc.)
- Melhor tratamento de erros
- Melhorias no código

## Créditos

- Baseado em engenharia reversa do aplicativo Android Udiconnect Plus (versão 4.8.8)
- Usa a API oficial Udiconnect Plus
- Desenvolvido para Home Assistant

## Aviso Legal

**IMPORTANTE: Leia atentamente antes de usar**

Esta é uma integração **não oficial** criada através de engenharia reversa para fins de interoperabilidade e uso pessoal. Este projeto:

- **NÃO é afiliado, endossado ou conectado** à Udiconnect Plus, Udinese, ASSA ABLOY ou qualquer uma de suas subsidiárias ou afiliadas
- **NÃO redistribui código proprietário** - apenas interage com APIs públicas
- É fornecido **"como está"**, sem garantias de qualquer tipo
- É destinado **exclusivamente para uso pessoal, educacional e de interoperabilidade**
- Pode violar os Termos de Serviço da Udiconnect Plus (verifique antes de usar)

### Responsabilidade do Usuário

Ao usar esta integração, você reconhece que:

1. **Uso por sua conta e risco**: O desenvolvedor não se responsabiliza por:
   - Danos aos seus dispositivos
   - Perda de acesso à sua conta Udiconnect Plus
   - Violação de termos de serviço
   - Qualquer outro dano direto ou indireto

2. **Conformidade Legal**: É sua responsabilidade verificar se o uso desta integração está em conformidade com:
   - Os Termos de Serviço da Udiconnect Plus
   - As leis aplicáveis em sua jurisdição
   - Quaisquer acordos que você tenha com o fabricante

3. **Uso Não Comercial**: Esta integração é destinada apenas para uso pessoal/doméstico. Uso comercial não é autorizado.

### Propósito e Escopo

Esta integração foi desenvolvida para permitir que usuários controlem seus próprios dispositivos em suas próprias residências através do Home Assistant, promovendo:

- **Interoperabilidade**: Integração com plataformas de automação residencial
- **Privacidade**: Controle local através do Home Assistant
- **Acessibilidade**: Interface única para múltiplos dispositivos IoT

## Licença

Este projeto é licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

**Resumo da Licença MIT:**
- ✓ Uso comercial e privado permitido
- ✓ Modificação e distribuição permitidas
- ✓ Fornecido sem garantias
- ⚠ A licença e aviso de copyright devem ser incluídos em todas as cópias

## Histórico de Versões

- **1.0.0** (2026-01-03)
  - Lançamento inicial
  - Suporte para cortinas e persianas
  - Fluxo de configuração pela interface
  - Descoberta automática de dispositivos
  - Controle de posição (abrir, fechar, definir posição)

- **1.0.6** (2026-01-04)
  - Bug fixes
