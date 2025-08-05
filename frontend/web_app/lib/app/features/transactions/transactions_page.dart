import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../../provider/transaction_provider.dart';
import '../../../models/transaction.dart'; // Adjust import as needed

class TransactionsPage extends StatefulWidget {
  const TransactionsPage({super.key});

  @override
  State<TransactionsPage> createState() => _TransactionsPageState();
}

class _TransactionsPageState extends State<TransactionsPage> {
  late Future<void> _initFuture;
  int _sortColumnIndex = 0;
  bool _sortAscending = true;
  String _searchQuery = '';

  final DateFormat _dateFormat = DateFormat('yyyy-MM-dd');
  final NumberFormat _currencyFormat = NumberFormat.currency(symbol: '\$');
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    final provider = context.read<TransactionProvider>();
    _initFuture = provider.init();
    _searchController.addListener(() {
      setState(() {
        _searchQuery = _searchController.text.trim().toLowerCase();
      });
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _sort<T>(
    Comparable<T> Function(Transaction tx) getField,
    int columnIndex,
    bool ascending,
  ) {
    final provider = context.read<TransactionProvider>();
    provider.transactions.sort((a, b) {
      final aValue = getField(a);
      final bValue = getField(b);
      return ascending
          ? Comparable.compare(aValue, bValue)
          : Comparable.compare(bValue, aValue);
    });

    setState(() {
      _sortColumnIndex = columnIndex;
      _sortAscending = ascending;
    });
  }

  List<Transaction> _filterTransactions(List<Transaction> transactions) {
    if (_searchQuery.isEmpty) return transactions;
    return transactions.where((tx) {
      return tx.payee.name.toLowerCase().contains(_searchQuery) ||
          tx.account.name.toLowerCase().contains(_searchQuery) ||
          tx.category.categoryName.toLowerCase().contains(_searchQuery) ||
          (tx.memo?.toLowerCase().contains(_searchQuery) ?? false);
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<TransactionProvider>();

    return Scaffold(
      appBar: AppBar(title: const Text('Transactions')),
      body: FutureBuilder<void>(
        future: _initFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          }

          final transactions = provider.transactions;
          final filteredTransactions = _filterTransactions(transactions);

          return Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: [
                // Search bar
                TextField(
                  controller: _searchController,
                  decoration: InputDecoration(
                    hintText: 'Search...',
                    prefixIcon: const Icon(Icons.search),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Expanded(
                  child: filteredTransactions.isEmpty
                      ? const Center(child: Text('No transactions found'))
                      : LayoutBuilder(
                          builder: (context, constraints) {
                            return SingleChildScrollView(
                              scrollDirection: Axis.horizontal,
                              child: ConstrainedBox(
                                constraints: BoxConstraints(
                                  minWidth: constraints.maxWidth,
                                ),
                                child: DataTable(
                                  sortColumnIndex: _sortColumnIndex,
                                  sortAscending: _sortAscending,
                                  columns: [
                                    DataColumn(
                                      label: const Text('Date'),
                                      onSort: (i, asc) =>
                                          _sort((tx) => tx.date, i, asc),
                                    ),
                                    DataColumn(
                                      label: const Text('Account'),
                                      onSort: (i, asc) => _sort(
                                        (tx) => tx.account.name,
                                        i,
                                        asc,
                                      ),
                                    ),
                                    DataColumn(
                                      label: const Text('Category'),
                                      onSort: (i, asc) => _sort(
                                        (tx) => tx.category.categoryName,
                                        i,
                                        asc,
                                      ),
                                    ),
                                    DataColumn(
                                      label: const Text('Payee'),
                                      onSort: (i, asc) =>
                                          _sort((tx) => tx.payee.name, i, asc),
                                    ),
                                    DataColumn(
                                      label: const Text('Memo'),
                                      onSort: (i, asc) =>
                                          _sort((tx) => tx.memo ?? '', i, asc),
                                    ),
                                    DataColumn(
                                      label: const Text('Amount'),
                                      numeric: true,
                                      onSort: (i, asc) =>
                                          _sort((tx) => tx.amount, i, asc),
                                    ),
                                  ],
                                  rows: List.generate(
                                    filteredTransactions.length,
                                    (index) {
                                      final tx = filteredTransactions[index];
                                      final amount =
                                          double.tryParse(tx.amount) ?? 0;
                                      final isIncome = amount > 0;
                                      return DataRow(
                                        color:
                                            MaterialStateProperty.resolveWith<
                                              Color?
                                            >((Set<MaterialState> states) {
                                              if (index % 2 == 0) {
                                                return Colors.grey.withOpacity(
                                                  0.05,
                                                );
                                              }
                                              return null;
                                            }),
                                        cells: [
                                          DataCell(
                                            Text(_dateFormat.format(tx.date)),
                                          ),
                                          DataCell(Text(tx.account.name)),
                                          DataCell(
                                            Text(tx.category.categoryName),
                                          ),
                                          DataCell(Text(tx.payee.name)),
                                          DataCell(Text(tx.memo ?? '')),
                                          DataCell(
                                            Text(
                                              _currencyFormat.format(amount),
                                              style: TextStyle(
                                                color: isIncome
                                                    ? Colors.green
                                                    : Colors.red,
                                                fontWeight: FontWeight.w600,
                                              ),
                                            ),
                                          ),
                                        ],
                                      );
                                    },
                                  ),
                                ),
                              ),
                            );
                          },
                        ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
