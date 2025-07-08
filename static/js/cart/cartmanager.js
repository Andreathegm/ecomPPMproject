// document.addEventListener('DOMContentLoaded', function () {
//     const updateButtons = document.querySelectorAll('.update-quantity');
//     let removeButtons = document.querySelectorAll('.btn-outline-danger');
//
//     const itemData = {};
//     document.querySelectorAll('.stock').forEach(input => {
//         const itemId = input.getAttribute('data-item-id');
//         const stock_value = parseInt(input.textContent.split(':')[1]);
//         const quantityInput = document.querySelector(`.quantity-input[data-item-id="${itemId}"]`);
//         const inputValue = parseInt(quantityInput.value);
//         if (inputValue === 1){
//             document.querySelector(`.update-quantity[data-item-id="${itemId}"][data-action="decrease"]`).classList.add('disabled');
//         }
//         if (inputValue === stock_value){
//             document.querySelector(`.update-quantity[data-item-id="${itemId}"][data-action="increase"]`).classList.add('disabled');
//         }
//         itemData[itemId] = {
//             stock_value: stock_value,
//             remaining_product: stock_value - inputValue,
//         };
//     });
//
//
//
//     updateButtons.forEach(button => {
//         button.addEventListener('click', function () {
//             const itemId = this.getAttribute('data-item-id');
//             const stock_value = itemData[itemId].stock_value;
//             const action = this.getAttribute('data-action');
//             const quantityInput = document.querySelector(`.quantity-input[data-item-id="${itemId}"]`);
//             const current_quantity = parseInt(quantityInput.value);
//             let plusQuantity = current_quantity + 1;
//             let minusQuantity = current_quantity - 1;
//             let newQuantity = 0
//             console.log(itemData[itemId].remaining_product, stock_value, current_quantity, plusQuantity, minusQuantity);
//
//
//
//             if (action === 'increase' && plusQuantity <= stock_value) {
//                 itemData[itemId].remaining_product--;
//                 newQuantity = plusQuantity;
//             }
//             else if (action === 'increase' && plusQuantity > stock_value){
//                 alert(`You can only order ${stock_value} items`);
//                 document.querySelector(`.update-quantity[data-item-id="${itemId}"][data-action="increase"]`).classList.add('disabled');
//                 newQuantity = current_quantity;
//
//             }
//             else if (action === 'decrease') {
//                 if (minusQuantity === 1) {
//                     document.querySelector(`.update-quantity[data-item-id="${itemId}"][data-action="decrease"]`).classList.add('disabled');
//
//                 }
//                 if (minusQuantity === stock_value-1) {
//                     document.querySelector(`.update-quantity[data-item-id="${itemId}"][data-action="increase"]`).classList.remove('disabled');
//
//                 }
//                 itemData[itemId].remaining_product++;
//                 newQuantity = minusQuantity;
//
//
//             }
//
//
//             // Update the quantity input field
//             quantityInput.value = newQuantity;
//
//             if (newQuantity > 1 && newQuantity < stock_value) {
//                 document.querySelector(`.update-quantity[data-item-id="${itemId}"][data-action="decrease"]`).classList.remove('disabled');
//                 document.querySelector(`.update-quantity[data-item-id="${itemId}"][data-action="increase"]`).classList.remove('disabled');
//
//             }
//
//             // Send AJAX request to update the quantity on the server
//             fetch(`/cart/update/${itemId}/`, {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                     'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
//                 },
//                 body: JSON.stringify({ quantity: newQuantity})
//             })
//                 .then(response => response.json())
//                 .then(data => {// Update the subtotal and total dynamically
//                     document.querySelector(`#subtotal-${itemId}`).textContent = `${data.subtotal}€`;
//                     document.querySelector('#cart-total').textContent = `${data.total}€`;
//                     document.querySelector('#cart-tax').textContent = `${data.tax}€`;
//                     document.querySelector('#cart-gran-total').textContent = `${data.grand_total}€`;
//                     document.querySelector(`#stock-${itemId}`).textContent = `Remaining: ${itemData[itemId].remaining_product}`;
//
//                     const d_subtotal = document.querySelector(`#d-subtotal-${itemId}`)
//                     if(d_subtotal){
//                         d_subtotal.textContent = `${data.discounted_subtotal}€`;
//                     }
//                     document.querySelector('#d-cart-total').textContent = `${data.discounted_total}€`;
//                     document.querySelector('#d-cart-tax').textContent = `${data.discounted_tax}€`;
//                     document.querySelector('#d-cart-gran-total').textContent = `${data.discounted_grand_total}€`
//
//                 })
//                 .catch(error => console.error('Error:', error));
//         });
//     });
//
//     removeButtons.forEach(button => {
//         button.addEventListener('click', function () {
//             const itemId = this.getAttribute('data-item-id');
//
//             // Send AJAX request to remove the item from the server
//             fetch(`/cart/remove/${itemId}/`, {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                     'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
//                 }
//             })
//                 .then(response => response.json())
//                 .then(data => {
//                     if (data.empty) {
//                         window.location.assign('/cart/');
//                         return;
//                     }
//                     // Remove the item row from the table
//                     document.querySelector(`#cart-item-row-${itemId}`).remove();
//
//                     // Update the total dynamically
//                     document.querySelector('#cart_icon_number').textContent = `${data.cart_items_count}`;
//                     document.querySelector('#cart-total').textContent = `${data.total}€`;
//                     document.querySelector('#cart-tax').textContent = `${data.tax}€`;
//                     document.querySelector('#cart-gran-total').textContent = `${data.grand_total}€`;
//                     document.querySelector(`#stock-${itemId}`).textContent = `Remaining: ${itemData[itemId].remaining_product}`;
//                     const d_subtotal = document.querySelector(`#d-subtotal-${itemId}`)
//                     if(d_subtotal){
//                         d_subtotal.textContent = `${data.discounted_subtotal}€`;
//                     }
//                     document.querySelector('#d-cart-total').textContent = `${data.discounted_total}€`;
//                     document.querySelector('#d-cart-tax').textContent = `${data.discounted_tax}€`;
//                     document.querySelector('#d-cart-gran-total').textContent = `${data.discounted_grand_total}€`
//
//                 })
//                 .catch(error => console.error('Error:', error));
//         });
//     });
// });
//
//
document.addEventListener('DOMContentLoaded', () => {
    const itemData = {};
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Funzioni helper
    const qs = (selector) => document.querySelector(selector);
    const qsa = (selector) => document.querySelectorAll(selector);

    const updateUI = (itemId, quantity, stockValue) => {
        const increaseBtn = qs(`.update-quantity[data-item-id="${itemId}"][data-action="increase"]`);
        const decreaseBtn = qs(`.update-quantity[data-item-id="${itemId}"][data-action="decrease"]`);

        increaseBtn.classList.toggle('disabled', quantity >= stockValue);
        decreaseBtn.classList.toggle('disabled', quantity <= 1);
    };

    const updateTotals = (data, itemId) => {
        qs(`#subtotal-${itemId}`).textContent = `${data.subtotal}€`;
        qs('#cart-total').textContent = `${data.total}€`;
        qs('#cart-tax').textContent = `${data.tax}€`;
        qs('#cart-gran-total').textContent = `${data.grand_total}€`;
        qs(`#stock-${itemId}`).textContent = `Remaining: ${itemData[itemId].remaining_product}`;

        const d_subtotal = qs(`#d-subtotal-${itemId}`);
        if (d_subtotal) d_subtotal.textContent = `${data.discounted_subtotal}€`;

        qs('#d-cart-total').textContent = `${data.discounted_total}€`;
        qs('#d-cart-tax').textContent = `${data.discounted_tax}€`;
        qs('#d-cart-gran-total').textContent = `${data.discounted_grand_total}€`;
    };

    // Inizializzazione dati stock
    qsa('.stock').forEach(el => {
        const itemId = el.dataset.itemId;
        const stockValue = parseInt(el.textContent.split(':')[1]);
        const input = qs(`.quantity-input[data-item-id="${itemId}"]`);
        const value = parseInt(input.value);

        itemData[itemId] = {
            stock_value: stockValue,
            remaining_product: stockValue - value,
        };

        updateUI(itemId, value, stockValue);
    });

    // Gestione aggiornamento quantità
    qsa('.update-quantity').forEach(button => {
        button.addEventListener('click', () => {
            const itemId = button.dataset.itemId;
            const action = button.dataset.action;
            const stockValue = itemData[itemId].stock_value;
            const input = qs(`.quantity-input[data-item-id="${itemId}"]`);
            let quantity = parseInt(input.value);

            if (action === 'increase') {
                if (quantity >= stockValue) {
                    alert(`You can only order ${stockValue} items`);
                    return;
                }
                quantity++;
                itemData[itemId].remaining_product--;
            } else if (action === 'decrease' && quantity > 1) {
                quantity--;
                itemData[itemId].remaining_product++;
            }

            input.value = quantity;
            updateUI(itemId, quantity, stockValue);

            showSpinner();

            fetch(`/cart/update/${itemId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ quantity })
            })
                .then(res => res.json())
                .then(data => updateTotals(data, itemId))
                .catch(err => console.error('Error:', err))
                .finally(() => {
                    hideSpinner();

                });
        });
    });

    // Gestione rimozione item
    qsa('.btn-outline-danger').forEach(button => {
        button.addEventListener('click', () => {
            const itemId = button.dataset.itemId;

            // Optional: mostra spinner
            showSpinner();

            fetch(`/cart/remove/${itemId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            })
                .then(res => res.json())
                .then(data => {
                    if (data.empty) {
                        window.location.assign('/cart/');
                        return;
                    }

                    qs(`#cart-item-row-${itemId}`)?.remove();
                    qs('#cart_icon_number').textContent = `${data.cart_items_count}`;
                    updateTotals(data, itemId);
                })
                .catch(err => console.error('Error:', err))
                .finally(() => {
                    hideSpinner()

                });
        });
    });
});
function showSpinner() {
    // 1. Crea il contenitore principale
    const overlay = document.createElement('div');
    overlay.id = 'loading-spinner';
    overlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center  bg-opacity-75';
    overlay.style.zIndex = '1050';

    // 2. Crea l’elemento spinner interno
    const spinner = document.createElement('div');
    spinner.className = 'spinner-border text-primary';
    spinner.setAttribute('role', 'status');
    spinner.style.width = '3rem';
    spinner.style.height = '3rem';

    // 3. Inserisci lo spinner dentro l’overlay
    overlay.appendChild(spinner);

    // 4. Appendi l’overlay al body
    document.body.appendChild(overlay);
}


function hideSpinner() {
    const overlay = document.getElementById('loading-spinner');
    if (overlay) {
        overlay.remove();
    }
}

