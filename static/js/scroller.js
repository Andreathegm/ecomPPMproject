function scrollCategories(direction) {
    const container = document.querySelector('.category-scroll-container');
    const scrollAmount = 320; // Card width (300px) + gap (20px)
    if (direction === 'left') {
        container.scrollLeft -= scrollAmount;
    } else {
        container.scrollLeft += scrollAmount;
    }
}