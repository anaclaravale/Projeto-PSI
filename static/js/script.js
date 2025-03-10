const selecionadosDiv = document.getElementById('selecionados');
const totalSpan = document.getElementById('total');
const form = document.getElementById('emprestimoForm');

// Adiciona os livros ao painel de seleção
document.querySelectorAll('.adicionar').forEach(button => {
    button.addEventListener('click', () => {
        const livroId = button.dataset.id;
        const titulo = button.dataset.titulo;
        const preco = parseFloat(button.dataset.preco);
        const estoque = parseInt(button.dataset.estoque);

        // Verifica se o livro já foi adicionado
        if (document.querySelector(`#livro-${livroId}`)) {
            alert('Este livro já foi adicionado!');
            return;
        }

        // Cria a nova div para o livro selecionado
        const div = document.createElement('div');
        div.id = `livro-${livroId}`;
        div.innerHTML = `
            <p>${titulo} (R$ ${preco.toFixed(2)})</p>
            <input type="hidden" name="livros" value="${livroId}">
            <label>Quantidade: </label>
            <input type="number" name="quantidades" min="1" value="1" max="${estoque}" class="quantidade" data-preco="${preco}" data-id="${livroId}" data-estoque="${estoque}">
            <button type="button" onclick="remover(${livroId})">Remover</button>
        `;
        selecionadosDiv.appendChild(div);

        // Atualiza o total sempre que um livro for adicionado
        atualizarTotal();
    });
});

// Função para remover o livro da lista
function remover(id) {
    const div = document.getElementById(`livro-${id}`);
    if (div) div.remove();

    // Atualiza o total após a remoção
    atualizarTotal();
}

// Função para atualizar o preço total do empréstimo
function atualizarTotal() {
    let total = 0;

    // Pega todos os inputs de quantidade
    const quantidades = document.querySelectorAll('.quantidade');
    quantidades.forEach(input => {
        let quantidade = parseInt(input.value);
        const preco = parseFloat(input.dataset.preco);
        const maxEstoque = parseInt(input.dataset.estoque);
        
        // Validações para evitar inconsistências
        if (isNaN(quantidade) || quantidade <= 0) {
            quantidade = 0; // Ignora valores inválidos
        } else if (quantidade > maxEstoque) {
            alert('A quantidade excede o estoque disponível!');
            input.value = maxEstoque; // Corrige para o estoque máximo
            quantidade = maxEstoque;
        }

        total += quantidade * preco;
    });

    // Exibe o total na tela
    totalSpan.textContent = total.toFixed(2);
}

// Adiciona um ouvinte de evento para monitorar alterações nas quantidades dos livros
document.addEventListener('input', function(event) {
    if (event.target.classList.contains('quantidade')) {
        atualizarTotal();
    }
});

// Código para ocultar mensagens de flash após 3 segundos
setTimeout(function() {
    var flashContainer = document.getElementById("flash-container");
    if (flashContainer) {
        flashContainer.style.transition = "opacity 0.5s";
        flashContainer.style.opacity = "0";
        setTimeout(() => flashContainer.remove(), 500); //
    }
}, 3000);
