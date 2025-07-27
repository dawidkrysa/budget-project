import 'package:intl/intl.dart';
import 'payee.dart';
import 'account.dart';
import 'category.dart';

class Transaction {
  final String id;
  final String amount;
  final String budgetId;
  final DateTime date;
  final bool deleted;
  final String? memo;

  final Account account;
  final Category category;
  final Payee payee;

  Transaction({
    required this.id,
    required this.amount,
    required this.budgetId,
    required this.date,
    required this.deleted,
    required this.account,
    required this.category,
    required this.payee,
    this.memo,
  });

  factory Transaction.fromJson(Map<String, dynamic> json) {
    return Transaction(
      id: json['id'],
      amount: json['amount'],
      budgetId: json['budget_id'],
      date: parseDate(json['date']),
      deleted: json['deleted'] ?? false,
      memo: json['memo'],
      account: Account.fromJson(json['account']),
      category: Category.fromJson(json['category']),
      payee: Payee.fromJson(json['payee']),
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'amount': amount,
        'budget_id': budgetId,
        'date': date.toIso8601String(),
        'deleted': deleted,
        'memo': memo,
        'account': account.toJson(),
        'category': category.toJson(),
        'payee': payee.toJson(),
      };

  static DateTime parseDate(dynamic raw) {
    if (raw is DateTime) return raw;

    if (raw is String) {
      // 1) try ISO-8601 first
      final iso = DateTime.tryParse(raw);
      if (iso != null) return iso;

      // 2) try RFC1123 like "Sun, 13 Jul 2025 00:00:00 GMT"
      try {
        final fmt = DateFormat("EEE, dd MMM yyyy HH:mm:ss 'GMT'", 'en_US');
        return fmt.parseUtc(raw);
      } catch (_) {/* fall through */}
    }

    throw ArgumentError('Unsupported date format: $raw');
  }
}
