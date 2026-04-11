document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("ingredient-input");
    const addButton = document.getElementById("add-ingredient");
    const chipList = document.getElementById("chip-list");
    const ingredientForm = document.getElementById("ingredient-form");
    const hiddenIngredients = document.getElementById("ingredients-json");

    if (!input || !addButton || !chipList || !ingredientForm || !hiddenIngredients) {
        return;
    }

    let ingredients = Array.from(chipList.querySelectorAll(".chip")).map((chip) => chip.dataset.ingredient);

    function syncHiddenField() {
        hiddenIngredients.value = JSON.stringify(ingredients);
    }

    function renderChip(value) {
        const chip = document.createElement("div");
        chip.className = "chip";
        chip.dataset.ingredient = value;

        const text = document.createElement("span");
        text.textContent = value;

        const remove = document.createElement("button");
        remove.type = "button";
        remove.setAttribute("aria-label", `Remove ${value}`);
        remove.textContent = "x";
        remove.addEventListener("click", () => {
            ingredients = ingredients.filter((ingredient) => ingredient !== value);
            chip.remove();
            syncHiddenField();
        });

        chip.append(text, remove);
        chipList.appendChild(chip);
    }

    function addIngredient() {
        const value = input.value.trim();
        if (!value) {
            return;
        }
        if (ingredients.includes(value)) {
            input.value = "";
            input.focus();
            return;
        }

        ingredients.push(value);
        renderChip(value);
        syncHiddenField();
        input.value = "";
        input.focus();
    }

    addButton.addEventListener("click", addIngredient);
    input.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            addIngredient();
        }
    });

    ingredientForm.addEventListener("submit", () => {
        // TODO: If you want an AJAX search flow instead of a normal form POST,
        // insert it here and send the ingredients array to your recipe logic.
        syncHiddenField();
    });

    chipList.addEventListener("click", (event) => {
        const button = event.target.closest("button");
        if (!button) {
            return;
        }

        const chip = button.closest(".chip");
        if (!chip) {
            return;
        }

        const value = chip.dataset.ingredient;
        ingredients = ingredients.filter((ingredient) => ingredient !== value);
        chip.remove();
        syncHiddenField();
    });

    syncHiddenField();
});
