// ==========================
// Global Variables
// ==========================
let mainURL = '/api/v1/budgets/ed903d5b-3ff2-4603-9f0a-d1061efd24f4' // TODO: To be replaced

// Function to initialize input listeners inside an accordion container
function initAccordionInputs(accordion) {
    accordion.querySelectorAll("input[type='number']").forEach(input => {
        input.addEventListener("change", event => {
            const input = event.target;
            if (input.value < 0) {
                input.value = 0;
            }

            const listItem = input.closest("li.list-group-item");
            const categoryName = listItem ? listItem.querySelector("span").textContent : "Unknown";

            fetch(mainURL + `/categories/${input.id}`, {
                method: 'PATCH',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({assigned: input.value})
            })
                .then(response => {
                    if (!response.ok) throw new Error('Failed to update');
                    return response.json();
                })
                .then(updatedData => {
                    console.log('Updated categories:', updatedData);
                    return fetch(window.location.href);  // fetch current page HTML
                })
                .then(response => response.text())
                .then(html => {
                    // Remember which collapse is open inside this accordion
                    const openItem = accordion.querySelector(".accordion-collapse.show");
                    const openId = openItem ? openItem.id : null;

                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');

                    // Find the updated accordion with the same ID in the fresh HTML
                    const newAccordion = doc.getElementById(accordion.id);

                    if (newAccordion) {
                        accordion.innerHTML = newAccordion.innerHTML;

                        // Re-initialize Bootstrap collapse and restore open state
                        if (openId) {
                            const newOpenItem = accordion.querySelector(`#${openId}`);
                            if (newOpenItem) {
                                const bsCollapse = new bootstrap.Collapse(newOpenItem, {toggle: false});
                                bsCollapse.show();
                            }
                        }

                        // Reattach event listeners after replacing innerHTML
                        initAccordionInputs(accordion);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert(`Error processing category "${categoryName}": ${error}`);
                });
        });
    });
}

// Initialize all accordions on page load
document.querySelectorAll('[id^="accordionFlushMain"]').forEach(accordion => {
    initAccordionInputs(accordion);
});
