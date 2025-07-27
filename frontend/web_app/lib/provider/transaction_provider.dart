import 'package:flutter/material.dart';
import 'package:web_app/services/transaction_service.dart';
import 'package:web_app/utils/debug_utils.dart';
import '../models/transaction.dart';

class TransactionProvider with ChangeNotifier {

  List<Transaction> _transactions = [];
  List<Transaction> get transactions => _transactions;

  final TransactionService _transactionService;

  TransactionProvider(this._transactionService);

  Future<void> init() async {
    try {
      _transactions = await _transactionService.fetchTransactions();
      notifyListeners();
    } catch (e) {
      DebugUtils.log(e.toString());
    }
  }

}