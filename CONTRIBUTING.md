# Guia de Contribuição

Este guia explica como contribuir com o projeto usando Git e GitHub.

## Pré-requisitos

- Git instalado (`git --version`).
- Conta no GitHub.
- (Opcional) GitHub CLI (`gh`).

## Fluxo de trabalho

### 1. Clonar o repositório

```bash
git clone https://github.com/<usuario>/biblioteca-digital.git
cd biblioteca-digital
```

### 2. Criar uma branch para sua contribuição

Nunca trabalhe direto na `main`. Crie uma branch descritiva:

```bash
git checkout -b feat/nome-da-funcionalidade
```

Prefixos sugeridos: `feat/` (novidade), `fix/` (correção), `docs/` (documentação).

### 3. Fazer commits claros (Conventional Commits)

Faça commits pequenos e frequentes, com mensagens no formato:

```
<tipo>: <descrição no imperativo>
```

Tipos: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`.

Exemplos:

```bash
git add src/biblioteca/catalogo.py
git commit -m "feat: adiciona busca por autor no catalogo"
```

### 4. Enviar a branch (push)

```bash
git push -u origin feat/nome-da-funcionalidade
```

### 5. Abrir um Pull Request (PR)

**Pela interface do GitHub:** acesse o repositório → "Compare & pull request" →
descreva o que mudou e por quê → "Create pull request".

**Pela linha de comando (GitHub CLI):**

```bash
gh pr create --title "feat: nome da funcionalidade" --body "Descrição das mudanças."
```

### 6. Revisão e merge

- Aguarde a revisão. Responda aos comentários com novos commits na mesma branch.
- Após aprovação, faça o merge do PR pela interface ou com:

```bash
gh pr merge --squash --delete-branch
```

## Padrão de qualidade

Antes de abrir o PR:

```bash
python -m pytest -v   # todos os testes devem passar
```

Mantenha o código no estilo PEP 8, com docstrings em português.
