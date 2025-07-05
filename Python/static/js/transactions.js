const transactionModal = document.getElementById('transactionModal');
transactionModal.addEventListener('shown.bs.modal', function () {
    const contentDiv = document.getElementById('transactionContent');
    contentDiv.innerHTML = 'Loading...';

    fetch('/api/v1/transaction_form_data')
        .then(res => res.json())
        .then(data => {
            // Build the form HTML dynamically:
            contentDiv.innerHTML = `
                  <form id="transactionForm">
                    <div class="mb-3">
                      <label for="transactionDate" class="form-label">Date</label>
                      <input type="date" class="form-control" id="transactionDate" name="date" value="${data.current_date || ''}" required>
                    </div>

                    <div class="mb-3">
                      <label for="transactionAccount" class="form-label">Account</label>
                      <select class="form-select" id="transactionAccount" name="account_id" required>
                        <option value="" disabled selected>Select account</option>
                        ${data.accounts.map(acc => `<option value="${acc.id}">${acc.name}</option>`).join('')}
                      </select>
                    </div>

                    <div class="mb-3">
                      <label for="transactionPayee" class="form-label">Payee</label>
                      <input type="text" class="form-control" id="transactionPayee" name="payee_name" list="payeeList" autocomplete="off" placeholder="Type or select payee" required>
                      <datalist id="payeeList">
                        ${data.payees.map(payee => `<option value="${payee.name}">`).join('')}
                      </datalist>
                    </div>

                    <div class="mb-3">
                      <label for="transactionCategory" class="form-label">Category</label>
                      <select class="form-select" id="transactionCategory" name="category_id">
                        <option value="" selected>-- None --</option>
                        ${data.categories.map(cat => `<option value="${cat.id}">${cat.name}</option>`).join('')}
                      </select>
                    </div>

                    <div class="mb-3">
                      <label for="transactionNote" class="form-label">Note</label>
                      <textarea class="form-control" id="transactionNote" name="memo" rows="2" placeholder="Optional note"></textarea>
                    </div>

                    <div class="mb-3">
                      <label for="transactionAmount" class="form-label">Amount</label>
                      <input type="number" step="0.01" min="0" class="form-control" id="transactionAmount" name="amount" placeholder="0.00" required>
                    </div>
                  </form>
                `;

        })
        .catch(error => {
            console.error('Error fetching data:', error);
            contentDiv.innerHTML = '<p class="text-danger">Failed to load data.</p>';
        });
});

const saveBtn = document.getElementById('addTransactionBtn');
saveBtn.addEventListener('click', () => {
  const form = document.getElementById('transactionForm');
  if (!form.checkValidity()) {
    form.reportValidity();
    return; // Stop if invalid
  }
  // Gather form data (example using FormData)
  const formData = new FormData(form);

  // Optionally convert FormData to JSON if your API expects JSON:
  const jsonData = {};
  formData.forEach((value, key) => {
    jsonData[key] = value;
  });

  // Call your API (adjust URL and options as needed)
  fetch('/api/v1/transactions/add', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(jsonData),
  })
  .then(response => {
    if (!response.ok) throw new Error('Network response was not ok');
    return response.json();
  })
  .then(data => {
    console.log('Transaction saved:', data);

    // Close the modal
    const modalElement = document.getElementById('transactionModal');
    const modalInstance = bootstrap.Modal.getInstance(modalElement);
    if (modalInstance) modalInstance.hide(); window.location.reload();

  })
  .catch(error => {
    console.error('Error submitting transaction:', error);
    // Show an error message to user if you want
  });
});

document.addEventListener('DOMContentLoaded', () => {
    const table = document.getElementById('transactions');
    const ths = table.querySelectorAll('thead th');
    const rows = Array.from(table.querySelectorAll('tbody tr'));

    ths.forEach((th, index) => {
        th.style.cursor = 'pointer';
        th.addEventListener('click', () => {
            const asc = th.classList.toggle('asc');
            ths.forEach(h => {
                if (h !== th) {
                    h.classList.remove('asc', 'desc');
                    h.querySelectorAll('.sort-icon').forEach(svg => svg.style.display = 'none');
                }
            });
            th.classList.toggle('desc', !asc);

            rows.sort((a, b) => {
                const aText = a.children[index].innerText.toLowerCase();
                const bText = b.children[index].innerText.toLowerCase();

                const aDate = Date.parse(aText);
                const bDate = Date.parse(bText);
                if (!isNaN(aDate) && !isNaN(bDate)) {
                    return asc ? aDate - bDate : bDate - aDate;
                }

                const aNum = parseFloat(aText.replace(',', '.'));
                const bNum = parseFloat(bText.replace(',', '.'));
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return asc ? aNum - bNum : bNum - aNum;
                }

                return asc ? aText.localeCompare(bText) : bText.localeCompare(aText);
            });

            const tbody = table.querySelector('tbody');
            rows.forEach(row => tbody.appendChild(row));

            // Show the correct SVG in the clicked header
            const upIcon = th.querySelector('.sort-icon-up');
            const downIcon = th.querySelector('.sort-icon-down');
            if (asc) {
                upIcon.style.display = 'inline-block';
                downIcon.style.display = 'none';
            } else {
                upIcon.style.display = 'none';
                downIcon.style.display = 'inline-block';
            }

        });
    });

    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', () => {
        const term = searchInput.value.toLowerCase();
        rows.forEach(row => {
            const match = Array.from(row.children).some(cell =>
                cell.innerText.toLowerCase().includes(term)
            );
            row.style.display = match ? '' : 'none';
        });
    });
});