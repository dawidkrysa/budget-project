// Select all number inputs inside your accordion
const inputs = document.querySelectorAll(".accordion input[type='number']");
inputs.forEach(input => {
  input.addEventListener("change", () => {
    // Find the closest list item (category)
    const listItem = input.closest("li.list-group-item");
    const categoryName = listItem ? listItem.querySelector("span").textContent : "Unknown";

    alert(`Input changed in category "${categoryName}": ${input.value}`);
  });
});