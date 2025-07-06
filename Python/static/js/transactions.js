/**
 * @fileoverview JavaScript for handling Transactions page functionality:
 * - Opening and submitting the add/edit transaction modal
 * - Fetching form data dynamically
 * - Table sorting and searching
 * - Deleting transactions with confirmation modal
 */

// ==========================
// Global Variables
// ==========================
let transactionMode = 'add'; // 'add' or 'edit'
let transactionIdToEdit = null; // Transaction ID being edited

// ==========================
// Modal Open Event Listeners
// ==========================

/**
 * Attach click listeners to all edit buttons to open the modal in edit mode.
 */
document.querySelectorAll('.editTransactionBtn').forEach(btn => {
    btn.addEventListener('click', () => {
        const transactionId = btn.dataset.id;
        openTransactionModal('edit', transactionId);
    });
});

/**
 * Attach click listeners to all add buttons to open the modal in add mode.
 */
document.querySelectorAll('.addTransactionBtn').forEach(btn => {
    btn.addEventListener('click', () => {
        openTransactionModal('add');
    });
});

// ==========================
// Open Transaction Modal
// ==========================

/**
 * Opens the transaction modal in the specified mode.
 * @param {'add'|'edit'} mode - Mode of the modal.
 * @param {string|null} transactionId - ID of the transaction to edit (if mode is 'edit').
 */
function openTransactionModal(mode, transactionId = null) {
    transactionMode = mode;
    transactionIdToEdit = transactionId;

    const modalElement = document.getElementById('transactionModal');
    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);

    // Set modal title
    const title = document.getElementById('transactionModalTitle');
    title.textContent = mode === 'edit' ? 'Edit transaction' : 'Add transaction';

    // Show modal
    modal.show();

    // Trigger 'shown.bs.modal' event manually to fetch form data
    modalElement.dispatchEvent(new Event('shown.bs.modal'));
}

// ==========================
// Load Form Data on Modal Show
// ==========================

const transactionModal = document.getElementById('transactionModal');

transactionModal.addEventListener('shown.bs.modal', function () {
    const contentDiv = document.getElementById('transactionContent');
    contentDiv.innerHTML = 'Loading...';

    // API endpoint depends on mode
    let fetchUrl = '/api/v1/transactions/form-data';
    if (transactionMode === 'edit') {
        fetchUrl = `/api/v1/transactions/${transactionIdToEdit}/form-data`;
    }

    fetch(fetchUrl)
        .then(res => res.json())
        .then(data => {
            // Dynamically build the form HTML
            contentDiv.innerHTML = `
                <form id="transactionForm">
                    <div class="mb-3">
                      <label for="transactionDate" class="form-label">Date</label>
                      <input type="date" class="form-control" id="transactionDate" name="date" value="${data.date || ''}" required>
                    </div>

                    <div class="mb-3">
                      <label for="transactionAccount" class="form-label">Account</label>
                      <select class="form-select" id="transactionAccount" name="account_id" required>
                        <option value="" disabled ${!data.account_id ? 'selected' : ''}>Select account</option>
                        ${data.accounts.map(acc =>
                            `<option value="${acc.id}" ${acc.id === data.account_id ? 'selected' : ''}>${acc.name}</option>`
                        ).join('')}
                      </select>
                    </div>

                    <div class="mb-3">
                      <label for="transactionPayee" class="form-label">Payee</label>
                      <input type="text" class="form-control" id="transactionPayee" name="payee_name" list="payeeList" autocomplete="off" placeholder="Type or select payee" value="${data.payee_name || ''}" required>
                      <datalist id="payeeList">
                        ${data.payees.map(payee => `<option value="${payee.name}">`).join('')}
                      </datalist>
                    </div>

                    <div class="mb-3">
                      <label for="transactionCategory" class="form-label">Category</label>
                      <select class="form-select" id="transactionCategory" name="category_id">
                        <option value="">-- None --</option>
                        ${data.categories.map(cat =>
                            `<option value="${cat.id}" ${cat.id === data.category_id ? 'selected' : ''}>${cat.name}</option>`
                        ).join('')}
                      </select>
                    </div>

                    <div class="mb-3">
                      <label for="transactionNote" class="form-label">Note</label>
                      <textarea class="form-control" id="transactionNote" name="memo" rows="2" placeholder="Optional note">${data.memo || ''}</textarea>
                    </div>

                    <div class="mb-3">
                      <label for="transactionAmount" class="form-label">Amount</label>
                      <input type="number" step="0.01" min="0" class="form-control" id="transactionAmount" name="amount" placeholder="0.00" value="${data.amount || ''}" required>
                    </div>
                </form>
            `;
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            contentDiv.innerHTML = '<p class="text-danger">Failed to load data.</p>';
        });
});

// ==========================
// Save Transaction (Add/Edit)
// ==========================

const saveBtn = document.getElementById('addTransactionBtn');

saveBtn.addEventListener('click', () => {
    const form = document.getElementById('transactionForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return; // Stop submission if form is invalid
    }

    // Gather form data
    const formData = new FormData(form);
    const jsonData = {};
    formData.forEach((value, key) => {
        jsonData[key] = value;
    });

    // Determine API endpoint and method
    let endpoint, method;
    if (transactionMode === 'add') {
        endpoint = '/api/v1/transactions';
        method = 'POST';
    } else {
        endpoint = `/api/v1/transactions/${transactionIdToEdit}`;
        method = 'PUT';
    }

    // Submit form data to API
    fetch(endpoint, {
        method,
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
            if (modalInstance) modalInstance.hide();

            // Reload page to update transaction list
            window.location.reload();
        })
        .catch(error => {
            console.error('Error submitting transaction:', error);
        });
});

// ==========================
// Table Sorting & Searching
// ==========================

document.addEventListener('DOMContentLoaded', () => {
    const table = document.getElementById('transactions');
    const ths = table.querySelectorAll('thead th');
    const rows = Array.from(table.querySelectorAll('tbody tr'));

    // Sorting functionality
    ths.forEach((th, index) => {
        th.style.cursor = 'pointer';
        th.addEventListener('click', () => {
            const asc = th.classList.toggle('asc');
            ths.forEach(h => {
                if (h !== th) {
                    h.classList.remove('asc', 'desc');
                    h.querySelectorAll('.sort-icon').forEach(svg => (svg.style.display = 'none'));
                }
            });
            th.classList.toggle('desc', !asc);

            rows.sort((a, b) => {
                const aText = a.children[index].innerText.toLowerCase();
                const bText = b.children[index].innerText.toLowerCase();

                // Date comparison
                const aDate = Date.parse(aText);
                const bDate = Date.parse(bText);
                if (!isNaN(aDate) && !isNaN(bDate)) {
                    return asc ? aDate - bDate : bDate - aDate;
                }

                // Numeric comparison
                const aNum = parseFloat(aText.replace(',', '.'));
                const bNum = parseFloat(bText.replace(',', '.'));
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return asc ? aNum - bNum : bNum - aNum;
                }

                // Text comparison fallback
                return asc ? aText.localeCompare(bText) : bText.localeCompare(aText);
            });

            const tbody = table.querySelector('tbody');
            rows.forEach(row => tbody.appendChild(row));

            // Toggle sorting icons visibility
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

    // Search functionality
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', () => {
        const term = searchInput.value.toLowerCase();
        rows.forEach(row => {
            const match = Array.from(row.children).some(cell => cell.innerText.toLowerCase().includes(term));
            row.style.display = match ? '' : 'none';
        });
    });

    // ==========================
    // Delete Transaction
    // ==========================

    const deleteModal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
    let transactionIdToDelete = null;

    document.querySelectorAll('.deleteTransactionBtn').forEach(btn => {
        btn.addEventListener('click', () => {
            transactionIdToDelete = btn.getAttribute('data-id');
            deleteModal.show();
        });
    });

    document.getElementById('confirmDeleteBtn').addEventListener('click', () => {
        if (!transactionIdToDelete) return;

        fetch(`/api/v1/transactions/${transactionIdToDelete}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
        })
            .then(response => {
                if (!response.ok) throw new Error('Failed to delete');
                return response.json();
            })
            .then(data => {
                console.log('Deleted:', data);
                window.location.reload();
            })
            .catch(error => {
                console.error('Error deleting transaction:', error);
            });
    });
});
