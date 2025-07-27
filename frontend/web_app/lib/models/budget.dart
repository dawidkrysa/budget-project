class Budget {
  final String budgetId;
  final String name;

  Budget({
    required this.budgetId,
    required this.name,
  });

  factory Budget.fromJson(Map<String, dynamic> json) => Budget(
    budgetId: json['id'] as String,
    name: json['name'] as String,
  );
}