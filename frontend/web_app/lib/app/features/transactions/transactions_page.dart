import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../provider/transaction_provider.dart';

class TransactionsPage extends StatefulWidget {

  const TransactionsPage({super.key});

  @override
  State<TransactionsPage> createState() => _TransactionsPageState();
}

class _TransactionsPageState extends State<TransactionsPage> {

  late Future<void> _initFuture;

  @override
  void initState() {
    super.initState();
    final provider = context.read<TransactionProvider>();
    _initFuture = provider.init();
  }

  String _formatDate(DateTime date) {
    return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day
        .toString().padLeft(2, '0')}';
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
              if (transactions.isEmpty) {
                return const Center(child: Text('No transactions'));
              }
              return SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: DataTable(
                  columns: const [
                    DataColumn(label: Text('Date')),
                    DataColumn(label: Text('Account')),
                    DataColumn(label: Text('Category')),
                    DataColumn(label: Text('Payee')),
                    DataColumn(label: Text('Amount')),
                  ],
                  rows: transactions.map((tx) {
                    return DataRow(
                      cells: [
                        DataCell(Text(_formatDate(tx.date))),
                        DataCell(Text(tx.account.name)),
                        DataCell(Text(tx.category.categoryName)),
                        DataCell(Text(tx.payee.name)),
                        DataCell(Text(tx.amount)),
                      ],
                    );
                  }).toList(),
                ),
              );
            }
        )
    );
  }
}