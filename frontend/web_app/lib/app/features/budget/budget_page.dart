import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:web_app/utils/debug_utils.dart';

import '../../../models/budget.dart';
import '../../../provider/budget_provider.dart';
import '../../../services/budget_service.dart';

class BudgetPage extends StatefulWidget {
  const BudgetPage({super.key});

  @override
  State<BudgetPage> createState() => _BudgetPageState();
}

class _BudgetPageState extends State<BudgetPage> {

  late Future<void> _initFuture;

  @override
  void initState() {
    super.initState();
    final provider = context.read<BudgetProvider>();
    _initFuture = provider.init();
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<BudgetProvider>();

    return Scaffold(
      appBar: AppBar(title: const Text('Budgets')),
      body: FutureBuilder<void>(
        future: _initFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          }
          final budgets = provider.budgets;
          if (budgets.isEmpty) {
            return const Center(child: Text('No budgets'));
          }
          return GridView.builder(
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2, // Set the number of columns
              crossAxisSpacing: 8.0, // Set the spacing between columns
              mainAxisSpacing: 8.0, // Set the spacing between rows
            ),
            itemCount: budgets.length,
            itemBuilder: (context, index) {
              final budget = budgets[index];
              final isSelected = provider.selectedBudgetId == budget.budgetId;
              return Card(
                color: isSelected ? Colors.blue.shade50 : Colors.white,
                child: Center(
                  child: TextButton(
                    onPressed: () {
                      provider.selectBudget(budget);
                    },
                    child: Text(
                      budget.name,
                      style: TextStyle(
                        color: isSelected ? Colors.blue : Colors.black,
                        fontWeight:
                            isSelected ? FontWeight.bold : FontWeight.normal,
                      ),
                    ),
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
