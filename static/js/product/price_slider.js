document.addEventListener('DOMContentLoaded', () => {
    const priceRange     = document.getElementById('priceRange');
    const priceValue     = document.getElementById('priceValue');
    const decrementBtn   = document.getElementById('priceDecrement');
    const incrementBtn   = document.getElementById('priceIncrement');
    const step           = 1;

    // Synchronize display and input value
    function updateDisplay(value) {
        priceValue.textContent = value;
        priceRange.value = value;
    }

    // Slider drag or keyboard change
    priceRange.addEventListener('input', (e) => {
        updateDisplay(e.target.value);
    });

    // Minus button
    decrementBtn.addEventListener('click', () => {
        const current = Number(priceRange.value);
        const min     = Number(priceRange.min);
        const next    = Math.max(current - step, min);
        updateDisplay(next);
    });

    // Plus button
    incrementBtn.addEventListener('click', () => {
        const current = Number(priceRange.value);
        const max     = Number(priceRange.max);
        const next    = Math.min(current + step, max);
        updateDisplay(next);
    });
});
