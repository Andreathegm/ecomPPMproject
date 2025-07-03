document.addEventListener('DOMContentLoaded', function () {
    const updateButtons = document.querySelectorAll('.update-quantity');
    let removeButtons = document.querySelectorAll('.btn-outline-danger');

    const itemData = {};
    document.querySelectorAll('.stock').forEach(input => {
        const itemId = input.getAttribute('data-item-id');
        const stock_value = parseInt(input.textContent.split(':')[1]);
        const quantityInput = document.querySelector(`.quantity-input[data-item-id="${itemId}"]`);
        const inputValue = parseInt(quantityInput.value);
        if (inputValue === 1){
            document.querySelector(`.update-quantity[data-item-id="${itemId}"][data-action="decrease"]`).classList.add('disabled');
        }
        if (inputValue === stock_value){
            document.querySelector(`.update-quantity[data-item-id="${itemId}"][data-action="increase"]`).classList.add('disabled');
        }
        itemData[itemId] = {
            stock_value: stock_value,
            remaining_product: stock_value - inputValue,
        };
    });



    updateButtons.forEach(button => {
        button.addEventListener('click', function () {
            const itemId = this.getAttribute('data-item-id');
            const stock_value = itemData[itemId].stock_value;
            const action = this.getAttribute('data-action');
            const quantityInput = document.querySelector(`.quantity-input[data-item-id="${itemId}"]`);
            const current_quantity = parseInt(quantityInput.value);
            let plusQuantity = current_quantity + 1;
            let minusQuantity = current_quantity - 1;
            let newQuantity = 0
            console.log(itemData[itemId].remaining_product, stock_value, current_quantity, plusQuantity, minusQuantity);



            if (action === 'increase' && plusQuantity <= stock_value) {
                itemData[itemId].remaining_product--;
                newQuantity = plusQuantity;
            }
            else if (action === 'increase' && plusQuantity > stock_value){
                alert(`You can only order ${stock_value} items`);
                document.querySelector(`.update-quantity[data-item-id="${itemId}"][data-action="increase"]`).classList.add('disabled');
                newQuantity = current_quantity;

            }
            else if (action === 'decrease') {
                if (minusQuantity === 1) {
                    document.querySelector(`.update-quantity[data-item-id="${itemId}"][data-action="decrease"]`).classList.add('disabled');

                }
                if (minusQuantity === stock_value-1) {
                    document.querySelector(`.update-quantity[data-item-id="${itemId}"][data-action="increase"]`).classList.remove('disabled');

                }
                itemData[itemId].remaining_product++;
                newQuantity = minusQuantity;


            }


            // Update the quantity input field
            quantityInput.value = newQuantity;

            if (newQuantity > 1 && newQuantity < stock_value) {
                document.querySelector(`.update-quantity[data-item-id="${itemId}"][data-action="decrease"]`).classList.remove('disabled');
                document.querySelector(`.update-quantity[data-item-id="${itemId}"][data-action="increase"]`).classList.remove('disabled');

            }

            // Send AJAX request to update the quantity on the server
            fetch(`/cart/update/${itemId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ quantity: newQuantity})
            })
                .then(response => response.json())
                .then(data => {// Update the subtotal and total dynamically
                    document.querySelector(`#subtotal-${itemId}`).textContent = `${data.subtotal}€`;
                    document.querySelector('#cart-total').textContent = `${data.total}€`;
                    document.querySelector('#cart-tax').textContent = `${data.tax}€`;
                    document.querySelector('#cart-gran-total').textContent = `${data.grand_total}€`;
                    document.querySelector(`#stock-${itemId}`).textContent = `Remaining: ${itemData[itemId].remaining_product}`;

                })
                .catch(error => console.error('Error:', error));
        });
    });

    removeButtons.forEach(button => {
        button.addEventListener('click', function () {
            const itemId = this.getAttribute('data-item-id');

            // Send AJAX request to remove the item from the server
            fetch(`/cart/remove/${itemId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.empty) {
                        window.location.assign('/cart/');
                        return;
                    }
                    // Remove the item row from the table
                    document.querySelector(`#cart-item-row-${itemId}`).remove();

                    // Update the total dynamically
                    document.querySelector('#cart_icon_number').textContent = `${data.cart_items_count}`;
                    document.querySelector('#cart-total').textContent = `${data.total}€`;
                    document.querySelector('#cart-tax').textContent = `${data.tax}€`;
                    document.querySelector('#cart-gran-total').textContent = `${data.grand_total}€`;
                    document.querySelector(`#stock-${itemId}`).textContent = `Remaining: ${itemData[itemId].remaining_product}`;

                })
                .catch(error => console.error('Error:', error));
        });
    });
});


