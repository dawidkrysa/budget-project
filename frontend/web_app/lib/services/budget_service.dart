import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:web_app/utils/debug_utils.dart';
import '../models/budget.dart';

const String url = String.fromEnvironment('API_URL');

class BudgetService {
  final FlutterSecureStorage _storage;

  BudgetService({FlutterSecureStorage? storage})
      : _storage = storage ?? const FlutterSecureStorage();

  Future<void> saveSelected(String id) async {
    await _storage.write(key: 'selected_budget_id', value: id);
  }

  Future<String?> getSelected() async {
    return _storage.read(key: 'selected_budget_id');
  }

  Future<void> removeSelected() async {
    await _storage.delete(key: 'selected_budget_id');
  }

  Future<List<Budget>> fetchBudgets() async {
    final token = await _storage.read(key: 'jwt');  // get token from secure storage
    final uri = Uri.parse('$url/budgets');
     final response = await http.get(
      uri,
      headers: {
      if (token != null) 'Authorization': 'Bearer $token',
      'Content-Type': 'application/json', // optional, but good to add
      },
    );

    DebugUtils.log('GET $uri -> ${response.statusCode}');

    if (response.statusCode == 200) {
      final decoded = jsonDecode(response.body) as List<dynamic>;
      DebugUtils.log('Response: $decoded');
      return decoded
          .map((e) => Budget.fromJson(e as Map<String, dynamic>))
          .toList();
    } else {
      throw Exception(
        'Failed to load budgets: ${response.statusCode} ${response.body}',
      );
    }
  }
}