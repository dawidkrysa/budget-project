// ==========================
// Global Variables
// ==========================
let mainURL = '/api/v1/budgets/ed903d5b-3ff2-4603-9f0a-d1061efd24f4' // TODO: To be replaced

document.querySelector('#accordionFlushMain').addEventListener("change", event => {
  const input = event.target;
  if (input.matches("input[type='number']")) {
    const listItem = input.closest("li.list-group-item");
    const categoryName = listItem ? listItem.querySelector("span").textContent : "Unknown";


    const url = new URL(mainURL + '/categories', window.location.origin);
    url.searchParams.append('category_name', categoryName);

    fetch(url, {
      method: 'GET',
      headers: {'Content-Type': 'application/json'}
    })
    .then(response => {
      if (!response.ok) throw new Error('Failed to get');
      return response.json();
    })
    .then(data => {
      console.log('Categories:', data);
      if (data.length > 0) {
        const id = data[0].id;
        console.log(`Category ID: ${id}, updating assigned to ${input.value}`);
        return fetch(mainURL + `/categories/${id}`, {
          method: 'PATCH',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({assigned: input.value})
        });
      } else {
        throw new Error('No matching category found');
      }
    })
    .then(response => {
      if (!response.ok) throw new Error('Failed to update');
      return response.json();
    })
    .then(updatedData => {
      console.log('Updated categories:', updatedData);
      // alert(`Updated category "${categoryName}" to assigned=${input.value}`);
      return fetch('/');
    })
    .then(response => response.text())
    .then(html => {
      const openItem = document.querySelector("#accordionFlushMain .accordion-collapse.show");
      const openId = openItem ? openItem.id : null;

      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      const newAccordion = doc.querySelector('#accordionFlushMain');

      document.querySelector('#accordionFlushMain').innerHTML = newAccordion.innerHTML;

      if (openId) {
        const newOpenItem = document.querySelector(`#${openId}`);
        if (newOpenItem) {
          const bsCollapse = new bootstrap.Collapse(newOpenItem, { toggle: false });
          bsCollapse.show();
        }
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert(`Error processing category "${categoryName}": ${error}`);
    });
  }
});
