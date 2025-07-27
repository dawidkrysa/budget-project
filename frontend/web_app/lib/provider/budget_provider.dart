import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:web_app/services/budget_service.dart';
import 'package:web_app/utils/debug_utils.dart';
import '../models/budget.dart';

class BudgetProvider with ChangeNotifier {
  Budget? _selectedBudget;
  Budget? get selectedBudget => _selectedBudget;

  String? _selectedBudgetId; // store id directly
  String? get selectedBudgetId => _selectedBudgetId;

  List<Budget> _budgets = [];
  List<Budget> get budgets => _budgets;

  final BudgetService _budgetService;

  BudgetProvider(this._budgetService);

  Future<void> init() async {
    try {
      _selectedBudgetId = await _budgetService.getSelected();
      _budgets = await _budgetService.fetchBudgets();
      notifyListeners();
    } catch (e) {
      DebugUtils.log(e.toString());
    }
  }

  Future<void> selectBudget(Budget budget) async {
    _selectedBudget = budget;
    _selectedBudgetId = budget.budgetId;
    await _budgetService.saveSelected(budget.budgetId);
    notifyListeners();
  }

  Future<void> clear() async {
    _selectedBudget = null;
    _selectedBudgetId = null;
    await _budgetService.removeSelected();
    notifyListeners();
  }

}