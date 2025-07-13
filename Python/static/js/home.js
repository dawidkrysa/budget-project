document.querySelector('#accordionFlushMain').addEventListener("change", event => {
  const input = event.target;
  if (input.matches("input[type='number']")) {
    const listItem = input.closest("li.list-group-item");
    const categoryName = listItem ? listItem.querySelector("span").textContent : "Unknown";

    const year = '2025';
    const month = '7';

    const url = new URL('/api/v1/budgets', window.location.origin);
    url.searchParams.append('category_name', categoryName);
    url.searchParams.append('year', year);
    url.searchParams.append('month', month);

    fetch(url, {
      method: 'GET',
      headers: {'Content-Type': 'application/json'}
    })
    .then(response => {
      if (!response.ok) throw new Error('Failed to get');
      return response.json();
    })
    .then(data => {
      console.log('Budgets:', data);
      if (data.length > 0) {
        const id = data[0].id;
        console.log(`Budget ID: ${id}, updating assigned to ${input.value}`);
        return fetch(`/api/v1/budgets/${id}`, {
          method: 'PATCH',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({assigned: input.value})
        });
      } else {
        // alert(`No budget found for category "${categoryName}" (${year}-${month})`);
        throw new Error('No matching budget found');
      }
    })
    .then(response => {
      if (!response.ok) throw new Error('Failed to update');
      return response.json();
    })
    .then(updatedData => {
      console.log('Updated budget:', updatedData);
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
