class Organizer {
    constructor() {
        this.select_el = document.querySelector(".sort-category");
        this.select_el.addEventListener('change', (event) => {
            const selectedCategory = event.target.value;
            if (selectedCategory === "-1") {
                window.location.href = "/";
            } else {
                window.location.href = `/?sort_category=${selectedCategory}`;
            }
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    new Organizer();
});