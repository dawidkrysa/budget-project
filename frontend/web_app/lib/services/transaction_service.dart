import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:web_app/utils/debug_utils.dart';
import '../models/transaction.dart';

const String url = String.fromEnvironment('API_URL');

class TransactionService {
  final FlutterSecureStorage _storage;

  TransactionService({FlutterSecureStorage? storage})
      : _storage = storage ?? const FlutterSecureStorage();

  Future<List<Transaction>> fetchTransactions() async {
    final budgetId = await _storage.read(key: 'selected_budget_id');
    final token = await _storage.read(key: 'jwt');  // get token from secure storage
    final uri = Uri.parse('$url/budgets/$budgetId/transactions?expand=account,category,payee');

     final response = await http.get(
      uri,
      headers: {
      if (token != null) 'Authorization': 'Bearer $token',
      'Content-Type': 'application/json', // optional, but good to add
      },
    );

    DebugUtils.log('GET $uri -> ${response.statusCode}');

    if (response.statusCode == 200) {
      final List<dynamic> jsonList = json.decode(response.body);
      return jsonList
        .map((jsonItem) => Transaction.fromJson(jsonItem as Map<String, dynamic>))
        .toList();
    } else {
      throw Exception(
        'Failed to load transactions: ${response.statusCode} ${response.body}',
      );
    }
  }
}